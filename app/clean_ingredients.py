from pyforest import *
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from sklearn.decomposition import TruncatedSVD
from sklearn.manifold import TSNE
import urllib
import pickle

# READ IN DATA (FACE MOISTURIZERS AND CLEANSERS)
# ~Next Step: Expand to other Skincare categories~#
moist = pd.read_csv('../scrapy_skincare/dermstorescraper/dermstorescraper/spiders/derm_moisturizers.csv')
cleansers = pd.read_csv('../skincare/scrapy_skincare/dermstorescraper/dermstorescraper/spiders/derm_cleansers.csv')
treatments = pd.read_csv('../skincare/scrapy_skincare/dermstorescraper/dermstorescraper/spiders/derm_treatments.csv')

# Drop NAs
moist = moist.dropna().reset_index(drop=True)
cleansers = cleansers.dropna().reset_index(drop=True)
treatments = treatments.dropna().reset_index(drop=True)


# Remove Duplicate rows 
moist = moist.drop_duplicates(subset='name', keep="first")
cleansers = cleansers.drop_duplicates(subset='name', keep="first")
treatments = treatments.drop_duplicates(subset='name', keep="first")

# Add Column to specify type
moist['prod_type'] = 'Moisturizers'
cleansers['prod_type'] = 'Cleansers and Exfoliators'
treatments['prod_type'] = 'Treatments and Serums'

# Combine Dataframes
frames = [moist, cleansers, treatments]
df = pd.concat(frames)
df = df.reset_index(drop=True)

# Shuffle rows
df = df.sample(frac=1).reset_index(drop=True)


# Take random sample of dataframe to work with (speeds up selenium automation)
sample = df.sample(frac=0.1).reset_index(drop=True)

#Acquire webdriver and open it 
s = Service(r'PATH_TO_DRIVER') #download right version of driver
chrome_options = Options()
chrome_options.add_argument("--headless")
driver = webdriver.Chrome(service=s,chrome_options=chrome_options)

cleaned_ingreds = []
for i in range(len(sample.all_ingreds)): 
    driver.get('https://www.skincarisma.com/products/analyze?utf8=%E2%9C%93&product%5Bingredient%5D='+urllib.parse.quote_plus(sample.all_ingreds[i]))
    cleaned_ingreds.append(driver.find_element(By.CSS_SELECTOR,'div.card-body p:nth-of-type(2)').text)

sample['cleaned_ingreds'] = cleaned_ingreds

#------------------- FUNCTIONS --------------------

# Get all Ingredients
def list_of_ingreds(df):
    ALL_INGREDS = []

    for i in df.cleaned_ingreds:
        ingreds_list = i.split(', ')
        for j in ingreds_list:
            ALL_INGREDS.append(j)
    return sorted(set(ALL_INGREDS))


# Create Ingredient Matrix
def ingred_matrix(ALL_INGREDS, df):
    one_hot_list = [[0] * 0 for i in range(len(ALL_INGREDS))]
    for i in df['cleaned_ingreds']:
        k=0
        for j in ALL_INGREDS:
            if j in i:
                one_hot_list[k].append(1)
            else:
                one_hot_list[k].append(0)
            k+=1
    ingred_matrix = pd.DataFrame(one_hot_list).transpose()
    ingred_matrix.columns = [sorted(set(ALL_INGREDS))]
    
    return ingred_matrix

# TruncatedSVD and TSNE
def svd_tsne(ingred_matrix):
    svd = TruncatedSVD(n_components=150, n_iter = 1000, random_state = 6) # firstly reduce features to 150 with truncatedSVD - this suppresses some noise
    svd_features = svd.fit_transform(ingred_matrix)
    tsne = TSNE(n_components = 2, n_iter = 1000000, random_state = 6) # reduce 150 features to 2 using t-SNE with exact method
    return tsne.fit_transform(svd_features)


# Vectorize Ingredients 
INGREDIENT_MATRIX = ingred_matrix(list_of_ingreds(sample), sample)
TSNE_FEATURES = svd_tsne(INGREDIENT_MATRIX)
sample['X'] = TSNE_FEATURES[:, 0]
sample['Y'] = TSNE_FEATURES[:, 1]

#Export CSV (Full dataset and Product Names Dataset)
sample.to_csv('../data/sample_skincare.csv', index=False)
product_names = pd.DataFrame({'name':sample.name})
product_names.to_csv('../data/product_names.csv', header=False, index=False)
product_names = pd.read_csv ('../data/product_names.csv')
product_names.to_pickle('../data/product_names.pkl')

