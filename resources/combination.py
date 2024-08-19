from flask_smorest import Blueprint
from db import db
import pandas as pd
from models import UserModel
from models import CombinationModel
from models import ClotheModel
from flask import jsonify,request
from sklearn.cluster import KMeans
import numpy as np
from scipy.sparse import csr_matrix
from sklearn.metrics.pairwise import cosine_similarity, euclidean_distances
import urllib.request
import json
import os
import ssl

blp = Blueprint("Combinations", __name__, description="Operations on combinations")

@blp.route("/user/<int:user_id>/combinations", methods=["GET"])

def get_user_combinations(user_id):
    combinations = CombinationModel.query.filter_by(user_id=user_id).all()
    return jsonify([combination.to_dict() for combination in combinations]), 200


def create_survey_matrix():
    users = UserModel.query.all()
    user_ids = [user.id for user in users]
    survey_data = [user.survey for user in users]
    df = pd.DataFrame(survey_data, index=user_ids)
    return df



def create_unified_user_ratings(user_id):
    """
    Belirtilen kullanıcıya ait tüm kombinasyonları, kıyafetlerin type, size ve color özelliklerine göre
    birleştirerek birleştirilmiş bir user_ratings DataFrame'i oluşturur.
    Diğer kullanıcıların bu kombinasyonlara sahip olup olmadığını kontrol eder ve rating'lerini ekler.

    Args:
        user_id (int): Belirtilen kullanıcının ID'si.

    Returns:
        DataFrame: Birleştirilmiş kullanıcı rating'lerini içeren DataFrame.
    """
    # Tüm kullanıcıları ve kullanıcının kombinasyonlarını al
    all_users = UserModel.query.all()
    user_combinations = CombinationModel.query.filter_by(user_id=user_id).all()

    # Kullanıcıya ait kombinasyonları unique olarak tanımla
    unique_combos = set()
    for combo in user_combinations:
        attributes = []
        
        # Top özellikleri
        top_attributes = [combo.top.type, combo.top.color, combo.top.size]
        attributes.append(','.join(top_attributes))
        
        # Bottom özellikleri
        bottom_attributes = [combo.bottom.type, combo.bottom.color, combo.bottom.size]
        attributes.append(','.join(bottom_attributes))
        
        # Shoe özellikleri
        shoe_attributes = [combo.shoe.type, combo.shoe.color, combo.shoe.size]
        attributes.append(','.join(shoe_attributes))
        
        # Jacket varsa, jacket özellikleri
        if combo.jacket:
            jacket_attributes = [combo.jacket.type, combo.jacket.color, combo.jacket.size]
            attributes.append(','.join(jacket_attributes))
        
        # Tüm attributes'ları '+' ile ayır
        unique_combos.add('+'.join(attributes))

    # Kullanıcıları ve kombinasyonları kullanarak DataFrame oluştur
    df = pd.DataFrame(index=[user.id for user in all_users], columns=list(unique_combos))

    # Kullanıcının kombinasyonlarını ve diğer kullanıcıların ratinglerini doldur
    for combo in user_combinations:
        attributes = []
        top_attributes = [combo.top.type, combo.top.color, combo.top.size]
        attributes.append(','.join(top_attributes))
        bottom_attributes = [combo.bottom.type, combo.bottom.color, combo.bottom.size]
        attributes.append(','.join(bottom_attributes))
        shoe_attributes = [combo.shoe.type, combo.shoe.color, combo.shoe.size]
        attributes.append(','.join(shoe_attributes))
        if combo.jacket:
            jacket_attributes = [combo.jacket.type, combo.jacket.color, combo.jacket.size]
            attributes.append(','.join(jacket_attributes))
        combo_attributes = '+'.join(attributes)
        
        # Bu kombinasyona sahip olan tüm kullanıcılar için rating değerlerini doldur
        matching_combinations = CombinationModel.query.filter(
            CombinationModel.top.has(type=combo.top.type, color=combo.top.color, size=combo.top.size),
            CombinationModel.bottom.has(type=combo.bottom.type, color=combo.bottom.color, size=combo.bottom.size),
            CombinationModel.shoe.has(type=combo.shoe.type, color=combo.shoe.color, size=combo.shoe.size),
            (CombinationModel.jacket == None) if combo.jacket is None else CombinationModel.jacket.has(
                type=combo.jacket.type, color=combo.jacket.color, size=combo.jacket.size)
        ).all()


        for matching_combo in matching_combinations:
            rating = matching_combo.rating if matching_combo.rating is not None else None
            df.at[matching_combo.user_id, combo_attributes] = rating

    # NaN değerleri açıkça belirt
    df = df.fillna(value=np.nan)
    
    return df




def cluster_users(user_ratings, n_clusters):
    kmeans = KMeans(n_clusters=n_clusters, random_state=0)
    clusters = kmeans.fit_predict(user_ratings.fillna(2.5))
    return clusters


def enhanced_similarity(user_ratings):
    cosine_sim = cosine_similarity(user_ratings.fillna(2.5))
    euclidean_sim = 1 / (1 + euclidean_distances(user_ratings.fillna(2.5)))
    return (cosine_sim + euclidean_sim) / 2

def cluster_based_cosine_similarity(user_ratings, clusters):
    user_similarity_within_clusters = np.zeros((len(user_ratings), len(user_ratings)))
    enhanced_sim = enhanced_similarity(user_ratings)

    for cluster_id in np.unique(clusters):
        cluster_indices = np.where(clusters == cluster_id)[0]
        cluster_similarity = enhanced_sim[cluster_indices][:, cluster_indices]
        for i, idx1 in enumerate(cluster_indices):
            for j, idx2 in enumerate(cluster_indices):
                user_similarity_within_clusters[idx1, idx2] = cluster_similarity[i, j]

    return pd.DataFrame(user_similarity_within_clusters, index=user_ratings.index, columns=user_ratings.index)

def predict_ratings_with_clusters(user_ratings, user_similarity, clusters):
    rating_predictions = user_ratings.copy()
    user_indices = user_ratings.index

    # Convert sparse matrix to dense if feasible
    if isinstance(user_similarity, csr_matrix):
        user_similarity = user_similarity.toarray()

    for user in user_indices:
        user_cluster = clusters[user_indices.get_loc(user)]
        cluster_users = user_indices[clusters == user_cluster]

        for combo in user_ratings.columns:
            if pd.isna(user_ratings.loc[user, combo]):
                relevant_ratings = user_ratings.loc[cluster_users, combo].dropna()
                relevant_similarities = user_similarity[user_indices.get_loc(user), [user_indices.get_loc(u) for u in relevant_ratings.index]]

                if relevant_similarities.sum() == 0:
                    prediction = 0
                else:
                    prediction = np.dot(relevant_ratings, relevant_similarities) / relevant_similarities.sum()

                rating_predictions.loc[user, combo] = prediction


    

    return rating_predictions



@blp.route('/get_recommendations', methods=['GET'])
def get_recommendations():
    """
    Belirli bir kullanıcı için öneriler üreten endpoint.
    """
    
    user_id = request.json.get("user_id")
    
    # Survey Matrix ve Kullanıcı Değerlendirmeleri
    survey_matrix = create_survey_matrix()
    print(survey_matrix)
    
    unified_user_ratings = create_unified_user_ratings(user_id)
    print(unified_user_ratings)
    print(user_id)  # user_id'nin None olup olmadığını kontrol et
    
    if user_id not in unified_user_ratings.index:
        print(f"user_id {user_id} not found in unified_user_ratings")
    
    # Kullanıcının değerlendirmelerini al
    user_ratings = unified_user_ratings.loc[user_id]
    user_ratings = pd.DataFrame(user_ratings)
    print(type(user_ratings))
    print(user_ratings.head())

    # NaN değerlerin indekslerini bul
    nan_indices = user_ratings[user_ratings.isna().any(axis=1)].index

    # Cluster İşlemleri ve Tahmin Hesaplama
    n_clusters = 3  
    clusters = cluster_users(survey_matrix, n_clusters)
    print(clusters)
    
    user_similarity_within_clusters = cluster_based_cosine_similarity(survey_matrix, clusters)
    sparse_user_similarity_within_clusters = csr_matrix(user_similarity_within_clusters)

    predicted_ratings = predict_ratings_with_clusters(
        unified_user_ratings,
        sparse_user_similarity_within_clusters,
        clusters
    )

    # Önerilen kombinleri ve tahmini rating değerlerini listele
    recommended_combos_list = [{'combo': combo, 'rating': predicted_ratings.loc[user_id, combo]} for combo in nan_indices]

    # Sıralama (en yüksek ratingler önce gelecek şekilde)
    recommended_combos_list = sorted(recommended_combos_list, key=lambda x: x['rating'], reverse=True)

    # İlk top_n kombinasyonu döndür
    # recommended_combos_list = jsonify(recommended_combos_list) Bu satırı JSON yapısına çevirmemize gerek yok şu anda

    # Kullanıcının `rating` değeri `None` olan kombinlerini getir
    none_rated_combos = CombinationModel.query.filter_by(user_id=user_id, rating=None).all()
    
    matching_combos_with_ids = []

    # Recommended combos'u parçalayarak top, bottom, shoe ve jacket bilgilerini çıkaralım
    for recommended_combo in recommended_combos_list:
        combo_parts = recommended_combo["combo"].split("+")
        
        # Combo'nun parçalarını ayır ve özelliklerini bul
        combo_dict = {}
        for part in combo_parts:
            item_type, color, size = part.split(",")
            combo_dict[item_type.strip()] = {"color": color.strip(), "size": size.strip()}
        
        # None rating'e sahip kombinler arasında eşleşenleri bul
        for combo in none_rated_combos:
            top = ClotheModel.query.get(combo.top_id)
            bottom = ClotheModel.query.get(combo.bottom_id)
            shoe = ClotheModel.query.get(combo.shoe_id)
            jacket = ClotheModel.query.get(combo.jacket_id) if combo.jacket_id else None

            if (top.color == combo_dict.get("T-shirt", {}).get("color") and
                top.size == combo_dict.get("T-shirt", {}).get("size") and
                bottom.color == combo_dict.get("Pant", {}).get("color") and
                bottom.size == combo_dict.get("Pant", {}).get("size") and
                shoe.color == combo_dict.get("Shoe", {}).get("color") and
                shoe.size == combo_dict.get("Shoe", {}).get("size")):
                
                # Eğer jacket varsa, jacket'in de kontrol edilmesi gerekiyor
                if jacket:
                    if (jacket.color == combo_dict.get("Jacket", {}).get("color") and
                        jacket.size == combo_dict.get("Jacket", {}).get("size")):
                        matching_combos_with_ids.append({
                            'top_id': combo.top_id,
                            'bottom_id': combo.bottom_id,
                            'shoe_id': combo.shoe_id,
                            'jacket_id': combo.jacket_id
                        })
                else:
                    # Eğer jacket yoksa sadece üst, alt ve ayakkabı kontrol ediliyor
                    matching_combos_with_ids.append({
                        'top_id': combo.top_id,
                        'bottom_id': combo.bottom_id,
                        'shoe_id': combo.shoe_id
                    })

    return jsonify(matching_combos_with_ids)




def allowSelfSignedHttps(allowed):
    if allowed and not os.environ.get('PYTHONHTTPSVERIFY', '') and getattr(ssl, '_create_unverified_context', None):
        ssl._create_default_https_context = ssl._create_unverified_context

allowSelfSignedHttps(True)





@blp.route('/get_recommendations_phi', methods=['GET'])
def get_recommendation_phi():
    user_id = request.json.get("user_id")
    user_prompt = request.json.get("user_prompt")
    
    
    isWinter = False
    if "cold" or "cool" or "chilly" or "winter" or "Winter" or "Cool" or "Cold" in user_prompt :
        isWinter = True
        
        
    if isWinter:    
        # Retrieve the user's clothes from ClotheModel
        user_clothes = ClotheModel.query.filter_by(user_id=user_id).all()
    else:
        user_clothes = ClotheModel.query.filter_by(user_id=user_id).filter(ClotheModel.type != "Jacket").all()
    
    # Format clothes for the prompt
    clothes_list = []
    for i, cloth in enumerate(user_clothes, 1):
        clothes_list.append(f"{cloth.color} {cloth.type}: {cloth.id}")

    clothes_prompt = " - ".join(clothes_list)

    if isWinter:    
        # Construct the prompt
        prompt = f"Suggest 2 outfits from the following clothes, ensuring each outfit includes at least one upper (T-shirt, Sweatshirt, Shirt), one lower (Pant, Short), one Jacket and one Shoe. \
        Just give them as 4 consecutive numbers. Do not write anything else than numbers and commas. Do not use the same clothes in different outfits. \
        Clothes: {clothes_prompt} \
        Prompt: {user_prompt}"
        print(clothes_prompt)
    else:
       # Construct the prompt
        prompt = f"Suggest 2 outfits from the following clothes, ensuring each outfit includes at least one upper (T-shirt, Sweatshirt, Shirt), one lower (Pant, Short), and one Shoe. \
        Just give them as 3 consecutive numbers. Do not write anything else than numbers and commas. Do not use the same clothes in different outfits. \
        Clothes: {clothes_prompt} \
        Prompt: {user_prompt}"
        print(clothes_prompt)
       
    

    

    # Prepare the data for the API request
    data = {
        "messages": [
            {"role": "system", "content": "Assume that you are a shopping assistant who gives fashion advice."},
            {"role": "user", "content": prompt}
        ],
        "constraints": {
            "min_upper": 1,
            "min_lower": 1,
            "min_shoes": 1
        }
    }

    body = str.encode(json.dumps(data))

    # API endpoint and key
    url = 'https://Phi-3-mini-4k-instruct-hxdwm.swedencentral.models.ai.azure.com/v1/chat/completions'
    api_key = 'pAgGHzRr4fOGCukyVrl1g8QiRWxKgyWy'

    if not api_key:
        raise Exception("A key should be provided to invoke the endpoint")

    headers = {'Content-Type': 'application/json', 'Authorization': ('Bearer ' + api_key)}

    # Send the request
    req = urllib.request.Request(url, body, headers)

    try:
        response = urllib.request.urlopen(req)
        result = response.read().decode()

        # Parse the response as JSON
        json_data = json.loads(result)

        # Extract the content part
        content = json_data["choices"][0]["message"]["content"]

        # Return the content as JSON
        return jsonify({"content": content})
    
    except urllib.error.HTTPError as error:
        print("The request failed with status code: " + str(error.code))
        print(error.info())
        print(error.read().decode("utf8", 'ignore'))
        return jsonify({"error": str(error)}), error.code

   