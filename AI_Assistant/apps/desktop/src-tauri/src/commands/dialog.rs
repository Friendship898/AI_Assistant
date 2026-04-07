#[tauri::command]
pub fn pick_file() -> Result<String, String> {
    Err("Step0 placeholder: native file dialog is not implemented yet.".to_string())
}

