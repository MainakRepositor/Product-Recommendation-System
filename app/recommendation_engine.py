from pyforest import *
from sentence_transformers import SentenceTransformer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Description Embedders
def embed_description(df):
    X = np.array(df.product_description)
    text_data = X
    model = SentenceTransformer('distilbert-base-nli-mean-tokens')
    embeddings = model.encode(text_data, show_progress_bar=True)
    embed_data = embeddings
    X = np.array(embed_data)
    return pd.DataFrame(cosine_similarity(X))


# Create Recommender 
def recommender(search, df, ingred=False, description=False, product_count = 5):
    if(ingred):
        myItem = df[df.name == search]
        myItem.reset_index(drop=True, inplace=True)
        P1 = np.array([myItem.X.values, myItem.Y.values]).reshape(1, -1)
        cos_sim = []
        for i in range(len(df)):
            P2 = np.array([df['X'][i], df['Y'][i]]).reshape(-1, 1)
            cos_sim.append((np.dot(P1, P2)/(np.linalg.norm(P1)*np.linalg.norm(P2)))[0][0])
        
        index_recomm = pd.DataFrame(cos_sim, columns=['cosine_sim']).sort_values(by=['cosine_sim'],ascending=False).index.tolist()
        products_recomm =  df.loc[index_recomm]
                
    elif(description):
        cos_sim = embed_description(df)
        index = df.index[df['name'] == search][0]
        index_recomm = cos_sim.loc[index].sort_values(ascending=False).index.tolist()
        products_recomm =  df.loc[index_recomm]
        
    products_recomm = products_recomm[(products_recomm.name != search)]

    return products_recomm.head(product_count)


