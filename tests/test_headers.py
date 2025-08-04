def test_invalid_headers():
    test_cases = [
        ('{"Accept": 123}', "值类型错误: 键 'Accept' 的值必须是字符串类型"),
        ('["Invalid", "Array"]', "请求头必须是字典对象"),
        ('{MissingQuotes: value}', "JSON格式错误: Expecting property name"),
        ('{"ValidBut": "trailing comma",}', "JSON格式错误: Expecting property name")
    ]
    
    for data, expected_error in test_cases:
        response = client.post('/create-task', data={'headers': data})
        assert response.status_code == 400
        assert expected_error in response.json['message']