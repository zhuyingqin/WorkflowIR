use std::env;
use std::fs;
use std::path::{Path, PathBuf};

fn is_embeddable_resource(path: &Path, skill_md: &Path) -> bool {
    if !path.is_file() {
        return false;
    }
    let Some(name) = path.file_name().and_then(|name| name.to_str()) else {
        return false;
    };
    if path == skill_md {
        return false;
    }
    name.ends_with(".py") || name.ends_with(".sh") || name.ends_with(".md")
}

fn collect_resource_files(root: &Path, skill_md: &Path, output: &mut Vec<PathBuf>) {
    let Ok(entries) = fs::read_dir(root) else {
        return;
    };
    for entry in entries.filter_map(Result::ok) {
        let path = entry.path();
        if path.is_dir() {
            collect_resource_files(&path, skill_md, output);
        } else if is_embeddable_resource(&path, skill_md) {
            output.push(path);
        }
    }
}

fn path_for_include(path: &Path) -> String {
    path.components()
        .map(|component| component.as_os_str().to_string_lossy())
        .collect::<Vec<_>>()
        .join("/")
}

fn main() {
    let out_dir = env::var("OUT_DIR").unwrap();
    let out_path = Path::new(&out_dir);
    let assets_dir = Path::new("assets/skills");

    println!("cargo:rerun-if-changed=assets/skills");

    let mut skill_names: Vec<String> = Vec::new();
    let mut resource_entries: Vec<(String, String)> = Vec::new(); // (key, filename)

    if assets_dir.exists() {
        let mut dirs: Vec<_> = fs::read_dir(assets_dir)
            .expect("read assets/skills")
            .filter_map(Result::ok)
            .filter(|e| e.file_type().map_or(false, |t| t.is_dir()))
            .collect();
        dirs.sort_by_key(|e| e.file_name());

        let skills_out = out_path.join("skills");
        fs::create_dir_all(&skills_out).expect("create skills out dir");

        for entry in dirs {
            let skill_md = entry.path().join("SKILL.md");
            if skill_md.exists() {
                let name = entry.file_name().to_string_lossy().to_string();
                // Copy skill file to OUT_DIR so include_str! can reference it
                let dest = skills_out.join(format!("{name}.md"));
                fs::copy(&skill_md, &dest).expect("copy skill file");
                skill_names.push(name.clone());

                // Also embed helper files (.py, .sh, .md) recursively. This
                // keeps skill-local scripts/references available after the
                // bundled skill is extracted at runtime.
                let mut resources = Vec::new();
                collect_resource_files(&entry.path(), &skill_md, &mut resources);
                resources.sort();
                for file_path in resources {
                    let rel = file_path
                        .strip_prefix(entry.path())
                        .expect("resource below skill dir");
                    let dest = skills_out.join(&name).join(rel);
                    if let Some(parent) = dest.parent() {
                        fs::create_dir_all(parent).expect("create helper resource dir");
                    }
                    fs::copy(&file_path, &dest).expect("copy helper file");
                    let rel_str = path_for_include(rel);
                    let key = format!("{name}/{rel_str}");
                    let out_name = format!("{name}/{rel_str}");
                    resource_entries.push((key, out_name));
                }
            } else {
                // Directory without SKILL.md — treat as shared-references or similar
                // Embed direct .md files under it.
                let dir_name = entry.file_name().to_string_lossy().to_string();
                if let Ok(files) = fs::read_dir(entry.path()) {
                    for file in files.filter_map(Result::ok) {
                        let fname = file.file_name().to_string_lossy().to_string();
                        if fname.ends_with(".md") && file.file_type().map_or(false, |t| t.is_file()) {
                            let dest = skills_out.join(&dir_name).join(&fname);
                            if let Some(parent) = dest.parent() {
                                fs::create_dir_all(parent).expect("create shared resource dir");
                            }
                            fs::copy(file.path(), &dest).expect("copy shared file");
                            let key = format!("{dir_name}/{fname}");
                            let out_name = format!("{dir_name}/{fname}");
                            resource_entries.push((key, out_name));
                        }
                    }
                }
            }
        }
    }

    // Generate Rust source for bundled skills
    let mut code = String::from(
        "/// Bundled ARIS skills compiled into the binary.\n\
         pub static BUNDLED_SKILLS: &[(&str, &str)] = &[\n",
    );
    for name in &skill_names {
        code.push_str(&format!(
            "    (\"{name}\", include_str!(concat!(env!(\"OUT_DIR\"), \"/skills/{name}.md\"))),\n"
        ));
    }
    code.push_str("];\n\n");

    // Generate Rust source for bundled helper resources
    code.push_str(
        "/// Bundled helper files (Python/Shell scripts) for skills.\n\
         pub static BUNDLED_RESOURCES: &[(&str, &str)] = &[\n",
    );
    for (key, out_name) in &resource_entries {
        code.push_str(&format!(
            "    (\"{key}\", include_str!(concat!(env!(\"OUT_DIR\"), \"/skills/{out_name}\"))),\n"
        ));
    }
    code.push_str("];\n");

    fs::write(out_path.join("bundled_skills.rs"), code).expect("write bundled_skills.rs");

    println!(
        "cargo:warning=Embedded {} bundled skills, {} helper resources",
        skill_names.len(),
        resource_entries.len()
    );
}
