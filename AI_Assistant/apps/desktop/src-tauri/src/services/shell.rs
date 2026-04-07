#[tauri::command]
pub fn open_path(_path: String) -> Result<String, String> {
    Err("Step0 placeholder: shell integration is not implemented yet.".to_string())
}

