from nltk.tokenize import RegexpTokenizer
from stop_words import get_stop_words
import gensim
import string
import glob
import multiprocessing
import json
import logging
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)


cores = multiprocessing.cpu_count()

finetune = True
if finetune:
    pretrained_model_path = '../../../datasets/WebVision/models/word2vec/word2vec_model_webvision.model'
    model = gensim.models.Word2Vec.load(pretrained_model_path)


whitelist = string.letters + string.digits + ' '
instagram_text_data_path = '../../../datasets/SocialMedia/captions_resized_1M/cities_instagram/'
webvision_text_data_path = '../../../datasets/WebVision/'
wikipedia_text_data_path = '../../../datasets/Wikipedia/train_texts/'
model_path = '../../../datasets/MIRFLICKR25K/models/word2vec/word2vec_model_MIRFlickr_finetuned_half.model'
words2filter = ['rt','http','t','gt','co','s','https','http','tweet','markars_','photo','pictur','picture','say','photo','much','tweet','now','blog','wikipedia','google', 'flickr', 'figure', 'photo', 'image', 'homepage', 'url', 'youtube','wikipedia','google', 'flickr', 'figure', 'photo', 'image', 'homepage', 'url', 'youtube', 'images', 'blog', 'pinterest']
cities = ['london','newyork','sydney','losangeles','chicago','melbourne','miami','toronto','singapore','sanfrancisco']

size = 400 # vector size
min_count = 5 # minimum word count to 2 in order to give higher frequency words more weighting
iter = 25 # iterating over the training corpus x times
window = 8

#Initialize Tokenizer
tokenizer = RegexpTokenizer(r'\w+')
# create English stop words list
en_stop = get_stop_words('en')
# add own stop words
for w in words2filter:
    en_stop.append(w)
# Create p_stemmer of class PorterStemmer
# p_stemmer = PorterStemmer()
texts = [] #List of lists of tokens


def get_instacities1m():
    # -- LOAD DATA FROM INSTAGRAM --
    posts_text = []
    for city in cities:
        print "Loading InstaCities1M data from " + city
        for i, file_name in enumerate(glob.glob(instagram_text_data_path + city + "/*.txt")):
            caption = ""
            filtered_caption = ""
            file = open(file_name, "r")
            for line in file:
                caption = caption + line
            # Replace hashtags with spaces
            caption = caption.replace('#', ' ')
            # Keep only letters and numbers
            for char in caption:
                if char in whitelist:
                    filtered_caption += char

            posts_text.append(filtered_caption.decode('utf-8').lower())

    return posts_text


def get_mirflickr():
    # -- LOAD DATA FROM MIRFlickr --
    print "Loading MIRFlickr data"
    posts_text = []
    train_half_indices_ints = []
    # Read topics for only retrieval images
    train_half = '../../../datasets/MIRFLICKR25K/train_half.txt'
    with open(train_half) as f:
        train_half_indices = f.readlines()
    for q in train_half_indices:
        train_half_indices_ints.append(int(q))
    for file_name in glob.glob("/home/raulgomez/datasets/MIRFLICKR25K/filtered_topics/*.txt"):
        if int(file_name.split('/')[-1][:-4]) not in train_half_indices_ints:
            continue
        file = open(file_name, "r")
        lines = []
        for line in file:
            line = line.replace('\n', '').replace('\t', '').replace('\r', '')
            line = line.replace('plant_life','plant')
            lines.append(line)
        posts_text.append(lines[0].replace(',',' ') + ' ' + lines[1].replace(',',' '))
        file.close()
    return posts_text

def get_wikipedia():
    # -- LOAD DATA FROM WIKI --
    posts_text = []
    print "Loading Wikipedia data"
    for i, file_name in enumerate(glob.glob(wikipedia_text_data_path +  "/*.xml")):
        caption = ""
        filtered_caption = ""
        file = open(file_name, "r")
        for line in file:
            caption = caption + line
        # Replace hashtags with spaces
        caption = caption.replace('#', ' ')
        caption = caption.split('text>')[1][:-3]
        # Keep only letters and numbers
        for char in caption:
            if char in whitelist:
                filtered_caption += char

        posts_text.append(filtered_caption.decode('utf-8').lower())
        print filtered_caption.decode('utf-8').lower()
        print '\n---------------\n'
    return posts_text



def get_webvision():
    # -- LOAD DATA FROM WEBVISION --
    posts_text = []
    former_filename = ' '
    print "Loading WebVision data"
    file = open(webvision_text_data_path + 'info/train_meta_list_all.txt', "r")

    for line in file:

        filename = line.split(' ')[0]
        filename = filename.replace('google', 'google_json')
        filename = filename.replace('flickr', 'flickr_json')
        idx = int(line.split(' ')[1])

        if filename != former_filename:
            print filename
            json_data = open(webvision_text_data_path + filename)
            d = json.load(json_data)
            former_filename = filename

        caption = ''
        filtered_caption = ''

        if d[idx - 1].has_key('description'): caption = caption + d[idx - 1]['description'] + ' '
        if d[idx - 1].has_key('title'): caption = caption + d[idx - 1]['title'] + ' '
        if d[idx - 1].has_key('tags'):
            for tag in d[idx - 1]['tags']:
                caption = caption + tag + ' '

        # Replace hashtags with spaces
        caption = caption.replace('#', ' ')
        # Keep only letters and numbers
        for char in caption:
            if char in whitelist:
                filtered_caption += char

        posts_text.append(filtered_caption.decode('utf-8').lower())

    return posts_text

posts_text = get_mirflickr()

print "Number of posts: " + str(len(posts_text))

print "Creating tokens"
c= 0

for t in posts_text:

    c += 1
    if c % 10000 == 0:
        print c

    try:
        t = t.lower()
        #Gensim simple_preproces instead tokenizer
        tokens = gensim.utils.simple_preprocess(t)
        # remove stop words from tokens
        stopped_tokens = [i for i in tokens if not i in en_stop]
        # stem token
        # text = [p_stemmer.stem(i) for i in stopped_tokens]
        # add proceced text to list of lists
        texts.append(stopped_tokens)
    except:
        continue

posts_text = []

#Train the model
print "Training ..."
if finetune:
    print model.iter
    model.train(texts, total_examples=model.corpus_count, epochs=25, compute_loss=False)
else:
    model = gensim.models.Word2Vec(texts, size=size, min_count=min_count, workers=cores, iter=iter, window=window)

model.save(model_path)
print "DONE"