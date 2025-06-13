use std::fs;
use serde::Deserialize;
use std::error::Error;

#[derive(Debug, Deserialize)]
struct Config {
    url_route: String,
    is_debug: bool,
    sleep_time: i64,
    request_timeout: i64,
    bot_token: Option<String>,
    channel_id: Option<i64>,
}

fn load_config() -> Result<Config, Box<dyn Error>> {
    let config_str = fs::read_to_string("assets/config.json")?;
    let config: Config = serde_json::from_str(&config_str)?;
    return Ok(config)
}

fn main() {
    let cfg_result = load_config();
    if cfg_result.is_err() {
        println!("Error! {:?}", cfg_result.err());
        return;
    }
    println!("Cfg: {:?}", cfg_result.ok());
}
