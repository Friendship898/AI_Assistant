mod commands {
    pub mod dialog;
    pub mod shortcut;
    pub mod tray;
    pub mod window;
}

mod services {
    pub mod shell;
}

pub fn run() {
    tauri::Builder::default()
        .invoke_handler(tauri::generate_handler![
            commands::dialog::pick_file,
            commands::shortcut::register_shortcut,
            commands::tray::set_tray_visibility,
            commands::window::show_main_window,
            services::shell::open_path,
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}

