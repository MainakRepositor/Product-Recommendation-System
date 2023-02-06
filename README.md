# skincare-recommender
Content-based recommendation engine that recommends scraped Dermstore skincare products based on product ingredients and descriptions 🫧
     

## Architecture:
1) Skincare product data (Moisturizers, Treatments/Serums, Cleansurs/Exfoliators) scraped from [Dermstore](https://dermstore.com) using **Scrapy**
2) Ingredients standardized with [Skincarisma's Ingredient Analyzer Tool](https://skincarisma.com) using **Selenium Webriver**
3) Product ingredient and description texts vectorized using **BERT embeddings** and **TruncatedSVD/TSNE**
4) Products recommended based on highest **Cosine Similarity**


**My App:** https://colabcontent.streamlit.app/

## ✨ App Demo ✨

![Alt Text](final_skincare.gif)

