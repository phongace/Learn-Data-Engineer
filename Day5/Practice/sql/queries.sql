-- Kiểm tra số lượng bản ghi
SELECT
    COUNT(*)
FROM
    `project.dataset.table`;

-- Tổng hợp dữ liệu
SELECT
    column,
    COUNT(*)
FROM
    `project.dataset.table`
GROUP BY
    column;