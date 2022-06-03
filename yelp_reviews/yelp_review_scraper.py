from bs4 import BeautifulSoup
from pyparsing import alphas
import requests
import re
import csv

API_KEY = "KrlCoAsmMTGJftfD6uV-s7kSN0o-SG2anMcTrwP6G4szLC3AsKX-hbiVLqiBfMj371sNemBCzrN8zCHae5SgIp1jqoiExhvExitIroX4_mBzQgWVtxcXFdFQIkkNYnYx"

# Black-owned restaurants scrapper 
def get_black_owned():
    url = "https://seenthemagazine.com/25-black-owned-restaurants-in-metro-detroit/"
    soup = BeautifulSoup(requests.get(url).text, 'html.parser')

    restaurants = soup.find_all('h3')
    stripped_restaurants = []
    for r in restaurants[:27]:
        stripped_restaurants.append(r.text.strip())
    print('done scraping restaurants')
    return stripped_restaurants

    # stripped_restaurants = ['Peteet’s Famous Cheesecakes', 'House of Pure Vin', 'Sweet Potato Sensations', 'Detroit Sip', 'Ima Noodles', 'Good Cakes and Bakes', 'Kuzzo’s Chicken and Waffles', 'Savannah Blue', 'The Jamaican Pot', 'Detroit Soul', 'Yum Village', 'Baker’s Keyboard Lounge', 'City Wings', 'Le Culture Cafe', 'The Block Detroit', 'Dime Store', 'Ellis Island Tropical Tea', 'GO! Smoothies', 'Detroit Vegan Soul', 'Detroit Seafood Market', 'Flood’s Bar and Grille', 'Central Kitchen and Bar', 'Beans & Cornbread', 'Brix Wine & Charcuterie Boutique', 'Dilla’s Delights', 'They Say Restaurant', 'The Breakfast Loft']

# hyphenate the restaurants to match the yelp url format
def hyphenate(stripped_restaurants):
    hyphen_restaurants = []
    for restaurant in stripped_restaurants:
        str = ""
        for char in restaurant:
            if char.isalpha():
                str += char.lower()
            elif char == " ":
                str += "-"
            elif char == "&":
                str += "and"
        hyphen_restaurants.append(str)
    print('done hyphenating')
    return hyphen_restaurants

    # hyphen_restaurants = ['peteets-famous-cheesecakes', 'house-of-pure-vin', 'sweet-potato-sensations', 'detroit-sip', 'ima-noodles', 'good-cakes-and-bakes', 'kuzzos-chicken-and-waffles', 'savannah-blue', 'the-jamaican-pot', 'detroit-soul', 'yum-village', 'bakers-keyboard-lounge', 'city-wings', 'le-culture-cafe', 'the-block-detroit', 'dime-store', 'ellis-island-tropical-tea', 'go-smoothies', 'detroit-vegan-soul', 'detroit-seafood-market', 'floods-bar-and-grille', 'central-kitchen-and-bar', 'beans-and-cornbread', 'brix-wine-and-charcuterie-boutique', 'dillas-delights', 'they-say-restaurant', 'the-breakfast-loft']

def get_reviews(hyphen_restaurants, city):
    non_valid = []
    reviews = {}
    for restaurant in hyphen_restaurants[-12:-10]:
        print(restaurant)
        # create the restaurant's url using the hyphenated names and provided city
        url = f"https://www.yelp.com/biz/{restaurant}-{city}"
        soup = BeautifulSoup(requests.get(url).text, 'html.parser')

        review_information = {}
        reviews_list = []
        regex = r"(\d+)\sreviews"

        # extract comments, ratings, and review count from the restaurant's main Yelp page
        first_ten = soup.find_all('p', class_="comment__09f24__gu0rG")
        first_ten_stars = soup.find_all('div', class_="i-stars__09f24__M1AR7")
        num_reviews_extract = soup.find_all('span', class_='css-1fdy0l5')

        # skips restaurant if not in city/url does not exist
        if first_ten == []:
            print(f"{restaurant} is not in {city}")
            non_valid.append(restaurant)
            continue 

        # get the number of reviews using regex expression
        for review in num_reviews_extract:
            reg_input = re.findall(regex, review.text)
            if reg_input != []:
                num_reviews = int(reg_input[0])
                review_information['number of reviews'] = num_reviews
        print(f"{restaurant} has {num_reviews} reviews") 

        # builds a dictionary for the first 10 reviews
        for i in range(len(first_ten)):
            rating = first_ten_stars[i]['aria-label']
            review = first_ten[i].text.strip()
            review_d = {}
            review_d['rating'] = rating
            review_d['review'] = review
            reviews_list.append(review_d)

        # loops through the remaining reviews and adds to review dictionary
        # Note there are some descrepancies between the number of reviews scraped from the Yelp page header and the number 
        # returned from the scraping. I.e. sweet potato sensations has 135 reviews according to yelp, but the code returns 138 reviews.
        # This is due to the double counting of multiple reviews - let's say a user reviews a restaurant in 2014, then they review 
        # again in 2021, these reviews would be linked and the original review would be double counted.
        # Tried a couple of different duplicate remvoal strategies, but all of them resulted in lost data
        # If we do analysis with the resulatant csv files, prbably easiest to manually remove duplicates in excel
        counter = 10
        while num_reviews > counter:
            new_url = url + f"?start={str(counter)}"
            print(new_url)
            soup = BeautifulSoup(requests.get(new_url).text, 'html.parser')
            next_ten = soup.find_all('p', class_="comment__09f24__gu0rG")
            next_ten_stars = soup.find_all('div', class_="i-stars__09f24__M1AR7")

            for i in range(len(next_ten)):
                rating = next_ten_stars[i]['aria-label']
                review = next_ten[i].text.strip()
                
                review_d = {}
                review_d['rating'] = rating
                review_d['review'] = review
                reviews_list.append(review_d)

            counter += 10
        review_information['Yelp user reviews'] = reviews_list
        reviews[restaurant] = review_information

        # writes csv files for each restaurant
        filename = f"review_csvs/{restaurant}.csv"
        with open(filename, "w") as csvfile:
            csvwriter = csv.writer(csvfile)
            csvwriter.writerow(["rating", "review"])
            for subd in reviews[restaurant]['Yelp user reviews']:
                rat = subd['rating']
                rev = subd['review']
                csvwriter.writerow([rat, rev])
        print(f'done with {restaurant}')

    # prints number of reviews and the number of reviews scraped to see how many duplicates we have
    # writes csv file of reviews for each restaurant
    for key in reviews:
        print(key)
        print(reviews[key]['number of reviews'])
        print(len(reviews[key]['Yelp user reviews']))

    return non_valid

def main():
    print('starting')
    restaurants = get_black_owned()
    hyphenated_restaurants = hyphenate(restaurants)
    non_valid = get_reviews(hyphenated_restaurants, 'detroit')
    print(f"not valid restaurants: {non_valid}")
    print('done')

if __name__ == '__main__':
    main()