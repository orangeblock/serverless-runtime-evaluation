extern crate serde_json;

use serde_derive::{Deserialize, Serialize};
use serde_json::{Error, Value};

#[derive(Serialize, Deserialize)]
struct Output {
    status: u8,
}

pub fn main(args: Value) -> Result<Value, Error> {
    let output = Output { status: 200 };
    serde_json::to_value(output)
}
