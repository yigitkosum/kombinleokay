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



def create_unified_user_ratings():
    """
    Kullanıcıların tüm kombinasyonlarını kıyafetlerin type, size ve color özelliklerine göre birleştirerek
    birleştirilmiş bir user_ratings DataFrame'i oluşturur.

    Returns:
        DataFrame: Birleştirilmiş kullanıcı rating'lerini içeren DataFrame.
    """
    # Bütün kullanıcıları ve kombinasyonları al
    all_users = UserModel.query.all()
    all_combinations = CombinationModel.query.all()

    # Kombinasyonları unique olarak tanımla
    unique_combos = set()
    for combo in all_combinations:
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

    # Kombinasyonları kullanıcılar ve ratingler ile doldur
    for combo in all_combinations:
        # Kombinasyonun özelliklerini oluştur
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
        
        # Rating değerini al
        rating = combo.rating if combo.rating is not None else np.nan

        # DataFrame'e rating'i ekle
        df.at[combo.user_id, combo_attributes] = rating

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



@blp.route('/get_predicted_ratings', methods=['GET'])
def get_recommendations():
    """
    Belirli bir kullanıcı için öneriler üreten endpoint.
    """
    
    user_id = request.json.get("user_id")

    

    survey_matrix = create_survey_matrix()
    print(survey_matrix)
    unified_user_ratings = create_unified_user_ratings()
    print(unified_user_ratings)
    print(user_id)  # user_id'nin None olup olmadığını kontrol et
    if user_id not in unified_user_ratings.index:
        print(f"user_id {user_id} not found in unified_user_ratings")
    

    # Kullanıcının değerlendirmelerini al
    user_ratings = unified_user_ratings.loc[user_id]
    
    user_ratings = pd.DataFrame(user_ratings)
    print(type(user_ratings))
    print(user_ratings.head())

    # nan değerlerin indekslerini bul
    nan_indices = user_ratings[user_ratings.isna().any(axis=1)].index

   
    n_clusters = 3  
    clusters = cluster_users(survey_matrix, n_clusters)
    print(clusters)
    user_similarity_within_clusters = cluster_based_cosine_similarity(survey_matrix, clusters)
    sparse_user_similarity_within_clusters = csr_matrix(user_similarity_within_clusters)

    # Tahminleri hesapla
    predicted_ratings = predict_ratings_with_clusters(
        unified_user_ratings,
        sparse_user_similarity_within_clusters,
        clusters
    )

    

    recommended_combos_list = [{'combo': combo, 'rating': predicted_ratings.loc[user_id, combo]} for combo in nan_indices]

# Sıralama (en yüksek ratingler önce gelecek şekilde)
    recommended_combos_list = sorted(recommended_combos_list, key=lambda x: x['rating'], reverse=True)

    # İlk top_n kombinasyonu döndür
    
    return jsonify(recommended_combos_list)
#jsonify({'recommendations': recommended_combos.index[:top_n].tolist()})
