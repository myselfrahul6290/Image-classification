#!pip install streamlit
from keras_vggface.utils import preprocess_input
from keras_vggface.vggface import VGGFace
import pickle
from sklearn.metrics.pairwise import cosine_similarity
import streamlit as st
from PIL import Image
import os
import cv2
from mtcnn import MTCNN
import numpy as np

detector = MTCNN()
model = VGGFace(model='resnet50',include_top=False,input_shape=(224,224,3),pooling='avg')
feature_list = pickle.load(open('embedding.pkl','rb'))
filenames = pickle.load(open('filenames.pkl','rb'))

def save_uploaded_image(uploaded_image):
    try:
        with open(os.path.join('uploads',uploaded_image.name),'wb') as f:
            f.write(uploaded_image.getbuffer())
        return True
    except:
        return False

def extract_features(img_path,model,detector):
    img = cv2.imread(img_path)
    results = detector.detect_faces(img)

    x, y, width, height = results[0]['box']

    face = img[y:y + height, x:x + width]

    #  extract its features
    image = Image.fromarray(face)
    image = image.resize((224, 224))

    face_array = np.asarray(image)

    face_array = face_array.astype('float32')

    expanded_img = np.expand_dims(face_array, axis=0)
    preprocessed_img = preprocess_input(expanded_img)
    result = model.predict(preprocessed_img).flatten()
    return result

def recommend(feature_list,features,ind):
    similarity = []
    for i in range(len(feature_list)):
        similarity.append(cosine_similarity(features.reshape(1, -1), feature_list[i].reshape(1, -1))[0][0])

    index_pos = sorted(list(enumerate(similarity)), reverse=True, key=lambda x: x[1])[ind][0]
    return index_pos

st.title('Find Your Images..')

uploaded_image = st.file_uploader('Choose an image')

if uploaded_image is not None:
    # save the image in a directory
    if save_uploaded_image(uploaded_image):
        # load the image
        display_image = Image.open(uploaded_image)
        #create col
        col1 = st.columns(1)[0]
        with col1:
            st.header('Your uploaded image')
            st.image(display_image,width=150)

        # extract the features
        features = extract_features(os.path.join('uploads',uploaded_image.name),model,detector)
        # recommend
        index_pos = recommend(feature_list,features,0)
        # print("INDEX pos",index_pos)
        predicted_actor = " ".join(filenames[index_pos].split('\\')[1].split('_'))

        index_pos1 = recommend(feature_list, features, 1)
        # print("INDEX pos",index_pos)
        predicted_actor1 = " ".join(filenames[index_pos1].split('\\')[1].split('_'))
        st.header("Look Like...")
        col2, col3=st.columns(2)

        # Recommend Image display

        with col2:
            # st.header("Look like " + predicted_actor)
            st.image(filenames[index_pos],width=300)

        with col3:
            # st.header("Look like " + predicted_actor)
            st.image(filenames[index_pos1],width=300)

# Run command-> streamlit run app.py