use axum::{Router, extract::Json, routing::post};
use serde::Serialize;
use std::fs;
use std::net::SocketAddr;

fn load_token() -> String {
    let content = fs::read_to_string(".telegram.env").expect("Failed to read .telegram.env");
    for line in content.lines() {
        if line.starts_with("TELEGRAM_TOKEN=") {
            return line
                .split('=')
                .nth(1)
                .unwrap()
                .trim()
                .trim_matches('"')
                .to_string();
        }
    }
    panic!("Token not found in .telegram.env");
}

#[derive(Debug, Serialize)]
struct Payload<'a> {
    chat_id: i64,
    text: &'a str,
}

fn get_battery_info() -> String {
    let capacity = fs::read_to_string("/sys/class/power_supply/BAT1/capacity")
        .unwrap_or_else(|_| "Unknown".into())
        .trim()
        .to_string();
    let status = fs::read_to_string("/sys/class/power_supply/BAT1/status")
        .unwrap_or_else(|_| "Unknown".into())
        .trim()
        .to_string();
    format!("Battery: {}% ({})", capacity, status)
}

fn send_message(token: &str, chat_id: i64, text: &str) {
    let url = format!("https://api.telegram.org/bot{}/sendMessage", token);
    let _ = ureq::post(&url).send_json(Payload { chat_id, text });
}

async fn telegram_webhook(Json(payload): Json<serde_json::Value>) -> &'static str {
    let token = load_token();

    if let Some(message) = payload.get("message") {
        if let Some(text) = message["text"].as_str() {
            if text.starts_with("/battery") {
                if let Some(chat_id) = message["chat"]["id"].as_i64() {
                    let battery_text = get_battery_info();
                    send_message(&token, chat_id, &battery_text);
                }
            }
        }
    }

    "OK"
}

#[tokio::main]
async fn main() {
    let app = Router::new().route("/webhook", post(telegram_webhook));

    // Bind locally to port 7890
    let addr = SocketAddr::from(([127, 0, 0, 1], 7890));
    println!("Webhook server listening on {}", addr);

    let listener = tokio::net::TcpListener::bind(&addr).await.unwrap();
    axum::serve(listener, app).await.unwrap();
}
