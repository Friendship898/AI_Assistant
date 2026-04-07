#[tauri::command]
pub fn show_main_window() -> Result<String, String> {
    Ok("Step0 placeholder: main window command is wired.".to_string())
}

