use calamine::{open_workbook, Data, Reader, Xlsx};
#[test]
fn real_pr_673_internal_space_inline() {
    let mut workbook: Xlsx<_> = open_workbook("tests/whitespace_trim.xlsx").unwrap();
    let cells = workbook.worksheet_range("inlineStr").unwrap();
    assert_eq!(cells.get_value((2, 0)), Some(&Data::String("日期 时间".into())));
}
#[test]
fn real_pr_673_internal_space_shared() {
    let mut workbook: Xlsx<_> = open_workbook("tests/whitespace_trim.xlsx").unwrap();
    let cells = workbook.worksheet_range("SharedStrings").unwrap();
    assert_eq!(cells.get_value((2, 0)), Some(&Data::String("日期 时间".into())));
}
