pub(super) fn json_string(text: &str) -> String {
    let escaped: String = text
        .chars()
        .flat_map(|character| match character {
            '"' => vec!['\\', '"'],
            '\\' => vec!['\\', '\\'],
            other => vec![other],
        })
        .collect();
    format!("\"{escaped}\"")
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn quotes_and_backslashes_are_escaped() {
        assert_eq!(json_string(r#"a"b\c"#), r#""a\"b\\c""#);
    }
}
