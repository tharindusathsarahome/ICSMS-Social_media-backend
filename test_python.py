result = {
    '661bc29a82246fcaaab59d43': {'alert': {'_id': '661bc29a82246fcaaab59d43', 'keyword_ids': ['661b851282246fcaaab579d4'], 'author': 'Dummy Author 1', 'min_val': 20, 'max_val': 50, 'alert_type': 'Email'}, 'keywords': [{'_id': '661b851282246fcaaab579d4', 'sm_id': 'SM01', 'author': 'Dummy Author 1', 'keyword': 'Dummy Keyword 1'}]}, 
    '661bc29a82246fcaaab59d44': {'alert': {'_id': '661bc29a82246fcaaab59d44', 'keyword_ids': ['661b851282246fcaaab579d5', '661b851282246fcaaab579d4'], 'author': 'Dummy Author 2', 'min_val': 10, 'max_val': 30, 'alert_type': 'App'}, 'keywords': [{'_id': '661b851282246fcaaab579d4', 'sm_id': 'SM01', 'author': 'Dummy Author 1', 'keyword': 'Dummy Keyword 1'}, {'_id': '661b851282246fcaaab579d5', 'sm_id': 'SM01', 'author': 'Dummy Author 2', 'keyword': 'Dummy Keyword 2'}]}, 
    '661bc29a82246fcaaab59d45': {'alert': {'_id': '661bc29a82246fcaaab59d45', 'keyword_ids': ['661b851282246fcaaab579d6'], 'author': 'Dummy Author 3', 'min_val': 40, 'max_val': 60, 'alert_type': 'Email'}, 'keywords': [{'_id': '661b851282246fcaaab579d6', 'sm_id': 'SM01', 'author': 'Dummy Author 3', 'keyword': 'Dummy Keyword 3'}]}, 
    '661bc29a82246fcaaab59d46': {'alert': {'_id': '661bc29a82246fcaaab59d46', 'keyword_ids': ['661b851282246fcaaab579d7'], 'author': 'Dummy Author 4', 'min_val': 5, 'max_val': 25, 'alert_type': 'App'}, 'keywords': [{'_id': '661b851282246fcaaab579d7', 'sm_id': 'SM01', 'author': 'Dummy Author 4', 'keyword': 'Dummy Keyword 4'}]}, 
    '661bc29a82246fcaaab59d47': {'alert': {'_id': '661bc29a82246fcaaab59d47', 'keyword_ids': ['661b851282246fcaaab579d8', '661b851282246fcaaab579d6', '661b851282246fcaaab579d7'], 'author': 'Dummy Author 5', 'min_val': 35, 'max_val': 70, 'alert_type': 'Email'}, 'keywords': [{'_id': '661b851282246fcaaab579d6', 'sm_id': 'SM01', 'author': 'Dummy Author 3', 'keyword': 'Dummy Keyword 3'}, {'_id': '661b851282246fcaaab579d7', 'sm_id': 'SM01', 'author': 'Dummy Author 4', 'keyword': 'Dummy Keyword 4'}, {'_id': '661b851282246fcaaab579d8', 'sm_id': 'SM01', 'author': 'Dummy Author 5', 'keyword': 'Dummy Keyword 5'}]}
}

itemService = []

for key, value in result.items():
    keyword = value['keywords'][0]['keyword']
    alert_type = value['alert']['alert_type']
    min_val = value['alert']['min_val']
    max_val = value['alert']['max_val']
    author = value['alert']['author']

    item = {
        'keyword': keyword,
        'alerttype': alert_type,
        'min_val': min_val,
        'max_val': max_val,
        'author': author
    }

    itemService.append(item)

print(itemService)
