import json
import os
import re
import nltk
import collections

from nltk.corpus import stopwords
from wordcloud import WordCloud
from collections import Counter

import twitter_client as tc
import matplotlib.pyplot as plt


def remove_url_hastag_user(text):
    """Replace URLs found in a text string with nothing 
    (i.e. it will remove the URL from the string).

    Parameters
    ----------
    text : string
        A text string that you want to parse and remove urls.

    Returns
    -------
    The same txt string with url's removed.
    """
    text = re.sub(r"\bhttps:\S*\b", "", text)
    text = re.sub(r"\b\d*\b", "", text)
    text = re.sub(r"[^\w\s@#]", "", text)

    processed_text_list = text.split()
    # hashtags, usernames
    for i in range(0, len(processed_text_list)):
        word = processed_text_list[i]
        if '#' in word or '@' in word:
            processed_text_list[i] = ''

    processed_text_list = list(filter(lambda x: x != '', processed_text_list))
    
    #stemming the word
    sno = nltk.stem.SnowballStemmer('english')
    processed_text_list = [sno.stem(word) for word in processed_text_list]

    processed_text      = ' '.join(processed_text_list)

    return processed_text

def extract_english_word(txt):
    """Filter out Non-English word and common english stop words.

    Parameters
    ----------
    txt : string
        A text string that you want to filter out the Non-English lower case word and common english stop words.

    Returns
    -------
    The same txt string with Non-English word and common english stop words removed.
    """

    #set of common english stop words from nltk
    stop_words = stopwords.words('english')
    stop_words += ['https','year','years','rt','co','new','also','like','today']

    stop_words = set(stop_words)

    #regex for english words with length between 2 and 100 letters
    lower_case_english_regx = "[a-z]{2,100}"

    #filter out non-english words
    words = re.findall(lower_case_english_regx, txt.lower())


    #filter out common stop words
    words = [w for w in words if not w in stop_words] 
    return words

def user_word_count(user_id):
    """count the english word frequency of a given user from his retweet file

    Parameters
    ----------
    user_id : number/string
    user id of the desired user

    Returns
    -------
    return word frequency Counter object of user with user_id
    """
    
    file_path = "hardmaru_data_files/" + str(user_id) + "_retweets2019-10-01-2019-11-30.txt"
    
    # print(file_path)

    word_freq = collections.Counter()
    try:
        with open(file_path) as f:
            for line in f:

                data            = json.loads(line)

                # print("data load properly")
                #text for the retweet
                retweet_text    = data['full_text']
                #text of the original tweet
                original_text   = data['retweeted_status']['full_text']

                # print("field load properly")

                retweet_text_procssed   = remove_url_hastag_user(retweet_text)
                original_text_processed = remove_url_hastag_user(original_text)

                # print("text processed properly")

                retweet_word_list  = extract_english_word(retweet_text_procssed)
                original_word_list = extract_english_word(original_text_processed)

                word_freq = word_freq + collections.Counter(retweet_word_list) + collections.Counter(original_word_list)
    except:
        print(file_path)
        print("no file exist for this user {0}, skipping".format(str(user_id)))
        return word_freq

    return word_freq


def group_word_count(user_id_list):
    """count the english word frequency of a group of users

    Parameters
    ----------
    user_id_list : list of string/number
    a list of user id

    Returns
    -------
    return word frequency Counter object of this group of users id
    """
    
    word_freq = collections.Counter()
    for user in user_id_list:
        word_freq += user_word_count(user)

    return word_freq

def group_follower_count(user_id_list):
    """count the english word frequency of a group of users

    Parameters
    ----------
    user_id_list : list of string/number
    a list of user id

    Returns
    -------
    return word frequency Counter object of this group of users id
    """
    
    total_follower = {}
    for user in user_id_list:
        total_follower[user] = tc.get_user_follower_number(str(user))
        sorted_total_follower = sorted(total_follower, reverse=True, key=lambda x: total_follower[x])

    return sorted_total_follower

def cluster_word_frequency(word_vector):
    """calculate the word frequency of each word for a given cluster

    Parameters
    ----------
    word_vector: word vector count of a given cluster

    Returns
    -------
    return word frequency dictionary a given cluster
    frequency vector is calcualted as follow:
    for words in word_vector:
        word fequency = # of words/ total number of words in this cluster
    """

    sum = 0
    words_dict = dict(word_vector).keys()
    for word in words_dict:
        sum += word_vector[word]

    word_frequency_vector = {}
    for word in words_dict:
        word_frequency_vector[word] = word_vector[word]/sum

    return word_frequency_vector


def relative_word_frequency(cluster_word_freq_vector, global_word_freq_vector):
    """calculate the relative word frequency of a user with respect to a global
    word vector

    Parameters
    ----------
    word_vector: word vector count of a given cluster
    global_word_vector: global word vector

    Returns
    -------
    return relative word frequency dictionary a given user with respect to global word vector
    the relative frequency vector is calcualted as follow:
    for words in word_vector:
        if words is in global_word_vector then word_freq = f(word|cluster)/f(w|global)
        if words is not in globacl_word_vector then word_freq = f(word|cluster)
    """
    sno  = nltk.stem.SnowballStemmer('english')

    relative_frequency_vector_in_global  = {}
    relative_frequency_vector_not_global = {}

    cluster_word_dict   = dict(cluster_word_freq_vector).keys()
    global_word_dict    = global_word_freq_vector.keys()

    for word in cluster_word_dict:
        word_stem = sno.stem(word)        
        if word_stem in global_word_dict:
            word_relative_frequency = cluster_word_freq_vector[word]/global_word_freq_vector[word_stem]
            relative_frequency_vector_in_global[word] = word_relative_frequency
        else:
            # relative_frequency_vector[word] = cluster_word_freq_vector[word]
            relative_frequency_vector_not_global[word] = cluster_word_freq_vector[word]

    sorted_relative_frequency_vector_in_global  = {k: v for k, v in sorted(relative_frequency_vector_in_global.items(),reverse = True, key=lambda item: item[1])}
    sorted_relative_frequency_vector_not_global = {k: v for k, v in sorted(relative_frequency_vector_not_global.items(),reverse = True, key=lambda item: item[1])}

    return sorted_relative_frequency_vector_in_global,sorted_relative_frequency_vector_not_global

def global_word_vector():
    """calculate the global word frequency from file

    Parameters
    ----------
    global_word_vector: global word vector

    Returns
    -------
    return global word frequency vector
    """
    file_path          = "global_word.json"
    global_word_vector = {}
    total              = 0

    with open(file_path,encoding="utf8") as f:
        for line in f:
            line = line.strip().strip(',')
            if line != '':
                word, count = line.split(':')
                word        = word.replace("\"","").strip()

                sno  = nltk.stem.SnowballStemmer('english')
                word = sno.stem(word)
                
                count       = int(count)
                total       += count 

                if word in global_word_vector.keys():
                    global_word_vector[word] = global_word_vector[word] + count
                else:
                    global_word_vector[word] = count

    global_word_frequency = {k: v / total for k, v in global_word_vector.items()}

    return global_word_frequency

def global_word_vector_stat():
    """calculate stat of the global word table from file

    Returns
    -------
    return total word count and total count of the global word vector
    """
    file_path          = "global_word.json"
    global_word_vector = {}
    total              = 0
    word_count         = 0
    with open(file_path,encoding="utf8") as f:
        for line in f:
            line = line.strip().strip(',')
            if line != '':
                word, count = line.split(':')
                word        = word.replace("\"","").strip()

                if word == "decis":
                    print("found it")
                    print(sno.stem(word))

                count       = int(count)
                total       += count 

                sno  = nltk.stem.SnowballStemmer('english')
                word = sno.stem(word)



                if word in global_word_vector.keys():
                    global_word_vector[word] = global_word_vector[word] + count
                else:
                    global_word_vector[word] = count
                    word_count               += 1

if __name__ == '__main__':

    global_word_vector_stat()

    input("press enter to cont")
    

    user_group1 = {989251872107085824, 7352832, 911297187664949248, 892732157294030848, 734984179956338688, 817060288281202689, 1050529973751205888, 837133583558987776, 1698006024, 797433864, 977687191202693125, 839820726777544705, 775449094739197953, 913491951013564422, 1014112771334602753, 23359503, 2278664208, 245493776, 46701577, 165744660, 2920625175, 34220569, 239881246, 423065127, 1387514922, 211137580, 2210861, 111886381, 2800204849, 19740214, 383107127, 463249977, 41078332, 2541954109, 4764525630, 97275971, 109814340, 927837253, 3874714693, 29907525, 1240028228, 98073161, 3301643341, 335091279, 1214528593, 33836629, 1426476636, 2902658140, 2601869406, 2334129246, 1912724060, 228792418, 1329262027, 2882893927, 1218100328, 28131948, 419039343, 162293874, 1364265588, 2575413876, 4070765174, 1278890108, 811646204635287552, 806058672619212800, 737939022480297984, 14565508, 861909801554595840, 733640801914343425, 927712304367652865, 2885934216, 951237270044069888, 610552974, 722771089, 60801171, 116117652, 69258389, 1321687705, 2472624794, 1223401116, 2309105822, 274692257, 8442372, 70482598, 1581645991, 22399655, 103251112, 11766442, 1638141098, 36906151, 1616352942, 79440047, 2577596593, 819861340294524928, 202328756, 236796085, 1540897980, 6270652, 905399486, 149627584, 87612611, 35754180, 744564421, 174734024, 131375305, 929211084, 279602892, 887992016, 2319245521, 281177812, 4010683096, 44073696, 197684961, 2909296352, 2303004390, 1901662951, 1469058794, 14283504, 586559221, 109561078, 3187990776, 70098171, 162124540, 2658365180, 932805374, 35826432, 790183810973458432, 2420657924, 41446149, 1067925193249759233, 56872711, 888216099757490176, 1375825160, 742409434534715393, 730823445752258562, 292849420, 844700194197397506, 51590414, 238349071, 14137617, 824999721659936768, 46791955, 815941956446470144, 18850305, 14393114, 4603400475, 4843757851, 2233489694, 776033693471240192, 560473379, 25263396, 731538535795163136, 1720046887, 4744970022, 215399723, 2897178924, 52316976, 338526004, 1270400820, 18358070, 2360, 22821179, 89986875, 140980031, 721931072, 19658565, 973073339911569408, 593394503, 14009672, 10850122, 476582730, 328130890, 14450509, 19510090, 838292815, 66169171, 231759188, 805535743875563520, 65876824, 64734554, 34979681, 36018529, 947465066, 412628332, 202573676, 1461069679, 173117297, 2409516403, 74262901, 180993910, 1046611830, 337230205, 24053629, 800067317702881280, 844953243931291648, 249619330, 887953975068291072, 796584325, 1556664198, 937688847852417025, 788467623629500416, 1150890935464669185, 82364810, 2950677387, 1004334946230693890, 310881672, 76809614, 4013975440, 16984977, 95683474, 357134227, 232294292, 101810581, 154989972, 155425682, 129520541, 2711765406, 94199200, 508659617, 26970530, 598904227, 755877821671702528, 51257255, 17629607, 636023721, 130064294, 359956908, 167628717, 2895499182, 5620142, 14832563, 258031029, 3312108981, 235786679, 374218172, 379923901, 1658829246, 898805695, 12876222, 885528008, 42566089, 2235411914, 47864778, 72030668, 14337485, 4870078413, 246967759, 28734416, 96584656, 14596050, 1365971, 21815759, 2784575957, 1463354832, 10985942, 96999384, 947276762, 243683803, 16067035, 3021399517, 3432396252, 1980381, 359622624, 84902368, 14103014, 292343271, 782356086120742912, 815300326127534080, 791080241112514560, 21771755, 90787316, 4484386293, 334926329, 67949052}
    user_group2 = {788107483306942464, 811840379733606401, 783356145670852608, 2749534722, 882990352248037377, 7173, 1001114465692200960, 3314904071, 1889160704, 466400265, 23795212, 167834639, 11613712, 6490642, 197507094, 43685411, 14587429, 14245415, 2978637351, 366913586, 115557940, 251780149, 339501114, 492678204, 18018877, 280941116, 225138752, 252761153, 3999382594, 20402762, 14335052, 17634892, 24587852, 29773, 2465283662, 4071001, 1833561, 7794782, 1625821280, 178817640, 12087912, 44698222, 315636336, 16030323, 19037299, 13235832, 2834526333, 321061507, 6146692, 14740612, 52789379, 139952263, 736204423, 3092104835, 188888207, 14328463, 84547217, 4591129234, 13461, 15463062, 14435477, 934224026, 14161568, 2492917412, 15626406, 22197926, 755367, 39083, 10724012, 3270420139, 191580846, 14080177, 706477238, 1034306232, 2160805051, 77501115, 42472635, 190857410, 15192772, 108868806, 184983241, 125314761, 18032331, 19080399, 137667281, 7670482, 84043985, 1086717654, 14841047, 59512534, 6627032, 6515422, 14097633, 1342672099, 143813860, 96815847, 6857962, 29255412, 153196789, 517079290, 1118579966, 1472037631, 16640266, 15407883, 20048140, 88892707, 5706532, 14148390, 273375532, 731279155, 17673012, 20733754, 8470842, 191100226, 15270211, 17013577, 14875983, 60385618, 1963617619, 15994195, 160251730, 2577700700, 207881569, 162441059, 11107172, 251310447, 126068081, 472364403, 3379659130, 3404085119, 2877269376, 15011200, 40631172, 51757957, 236562313, 2460047754, 17035147, 858119568, 248151441, 14914457, 5812122, 3091349915, 2414683548, 18104734, 423671207, 96770474, 4020498861, 491407790, 2946570168, 3229830076, 2517832639, 38215107, 58558405, 3238924744, 76025806, 21084111, 64590803, 937467860, 14665172, 14381020, 1387915232, 18229224, 22133225, 5633002, 18246129, 3375167474, 448952307, 183655922, 3279241202, 283755001, 237920763, 1117107708, 15540222}
    user_group3 = {734995453813641216, 709543955126333440, 740238495952736256, 992153930095251456, 1076526138736951298, 957374995721629696, 872274950, 794346991627010048, 892059194240532480, 3728642057, 1408142352, 14699038, 21795879, 17661484, 6535212, 17595439, 2479063608, 386282560, 36515907, 2781430855, 198678609, 14470738, 4680572004, 9316452, 11518572, 339261041, 216939636, 2785337469, 76080258, 1236101, 194122373, 52247685, 34376328, 38708874, 101609102, 3259586191, 14710416, 14459551, 357786278, 56843433, 19387570, 2529971, 446659775, 42226885, 14427338, 14642896, 615818451, 14597344, 786148, 183791347, 42768627, 2413997304, 36749051, 332018940, 36153601, 149763, 493458695, 13634322, 622784277, 111060272, 14622002, 446719282, 28835645, 2286218053, 1442906958, 21066583, 39547749, 158106469, 14378343, 15363432, 96570221, 96135022, 18027886, 2573466488, 865622395, 122080635, 22674817, 2153743237, 274821510, 7319442, 254107028, 289610659, 257642411, 10476462, 4558314927, 15278016, 5659072, 14065609, 1547221, 2967221722, 86351835, 38398940, 823957466, 14080479, 68746721, 2178012643, 12451812, 9271782, 1071350252, 1478433775, 197313522, 1191207924}
    user_group4 = {769188626324398080, 875904936763998208, 2534045701, 337419400, 5904392, 5262991, 3848981, 188309022, 3356524452, 129510439, 2896013873, 9133362, 45851571, 305687859, 2180077237, 45786442, 1320611023, 3181519447, 91267548, 14497118, 122894436, 12483052, 45040370, 19596021, 4167551}
    
    user_collection = set(list(user_group1) + list(user_group2) + list(user_group3) + list(user_group4))
    
    global_word_freq = global_word_vector()

    user_group1_word_count = group_word_count(user_group1)
    user_group2_word_count = group_word_count(user_group2)
    user_group3_word_count = group_word_count(user_group3)

    user_group1_word_freq  = cluster_word_frequency(user_group1_word_count)
    user_group2_word_freq  = cluster_word_frequency(user_group2_word_count)
    user_group3_word_freq  = cluster_word_frequency(user_group3_word_count)


    user_group1_relative_word_frequency1, user_group1_relative_word_frequency2 = relative_word_frequency(user_group1_word_freq,global_word_freq)
    user_group2_relative_word_frequency1, user_group2_relative_word_frequency2 = relative_word_frequency(user_group2_word_freq,global_word_freq)
    user_group3_relative_word_frequency1, user_group3_relative_word_frequency2 = relative_word_frequency(user_group3_word_freq,global_word_freq)
    
    print(Counter(user_group1_relative_word_frequency1).most_common(20))
    print(Counter(user_group1_relative_word_frequency2).most_common(20))
    print(Counter(user_group2_relative_word_frequency1).most_common(20))
    print(Counter(user_group2_relative_word_frequency2).most_common(20))
    print(Counter(user_group3_relative_word_frequency1).most_common(20))
    print(Counter(user_group3_relative_word_frequency2).most_common(20))

    # plt.figure(1)
    # plt.hist(cluster1_follower_count, bins = 10)

    # plt.figure(2)
    # plt.hist(cluster2_follower_count, bins = 10)

    # plt.figure(3)
    # plt.hist(cluster3_follower_count, bins = 10)

    # plt.figure(4)
    # plt.hist(cluster4_follower_count, bins = 10)

    # plt.show()

    
    # word_freq1   = group_word_freq(user_group1)
    # word_freq2   = group_word_freq(user_group2)
    # word_freq3   = group_word_freq(user_group3)
    # print(word_freq1.most_common(100))
    # print(word_freq2.most_common(100))
    # print(word_freq3.most_common(100))

    # wordcloud  = WordCloud()

    # wordcloud.generate_from_frequencies(frequencies=user_group1_relative_word_frequency)
    # plt.figure(1)
    # plt.imshow(wordcloud, interpolation="bilinear")
    # plt.axis("off")


    # wordcloud.generate_from_frequencies(frequencies=user_group2_relative_word_frequency)
    # plt.figure(2)
    # plt.imshow(wordcloud, interpolation="bilinear")
    # plt.axis("off")


    # wordcloud.generate_from_frequencies(frequencies=user_group3_relative_word_frequency)
    # plt.figure(3)
    # plt.imshow(wordcloud, interpolation="bilinear")
    # plt.axis("off")
    # plt.show()