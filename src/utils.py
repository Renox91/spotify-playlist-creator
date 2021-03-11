def transform_json_artists_liked(data):
    new_data = []
    for item in data['artists']['items']:
        temp_dict = dict()
        temp_dict["name"] = item["name"]
        temp_dict["id"] = item["id"] 
        temp_dict['url_img'] = item['images'][0]["url"]
        temp_genres = ", ".join(item["genres"])

        if len(temp_genres) > 30:
            temp_dict['genres'] = temp_genres[0:30] + " ..."
            temp_dict['rest_genres'] = temp_genres
        else:
            temp_dict['genres'] = temp_genres
            temp_dict['rest_genres'] = ""
        
        temp_dict['followers'] = item['followers']["total"]
        new_data.append(temp_dict)

    return new_data