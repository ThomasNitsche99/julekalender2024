import streamlit as st
from streamlit_cookies_controller import CookieController
from st_supabase_connection import SupabaseConnection, execute_query
from datetime import datetime
import hashlib
import time
import uuid

st.set_page_config(
    page_title="Julekalender 2024",
    page_icon="🎅",
)

#Initialize connection to database
supabase_client = st.connection("supabase",type=SupabaseConnection)

#Initialize the cookie controller
cookie_controller = CookieController()

#Cookie expiration date
date_obj = datetime(2024, 12, 26)

# Get the current date and time
now = datetime.now()

# Extract the current month and date
current_month = now.month
current_date= str(now.day)


calendar = {
    "1": {"emojis": "🚬🏇", "answer": "sigrid"},
    "2": {"emojis": "🪙⬅️", "answer": "nickelback"},
    "3": {"emojis": "👶🏼🏎️", "answer": "unge ferrari"},
    "4": {"emojis": "🏇👧🏾", "answer": "rihanna"},
    "5": {"emojis": "🍑🌲S", "answer": "astrid s"},
    "6": {"emojis": "⬆️🪁", "answer": "highasakite"},
    "7": {"emojis": "🚪🚪🎥🪩", "answer": "two door cinema club"},
    "8": {"emojis": "⬅️🛣️🙍‍♂️🙍‍♂️", "answer": "backstreet boys"},
    "9": {"emojis": "🐫", "answer": "kamelen"},
    "10": {"emojis": "🐘🥅🛎️", "answer": "ellie goulding"},
    "11": {"emojis": "💭🐲", "answer": "imagine dragons"},
    "12": {"emojis": "👸", "answer": "queen"},
    "13": {"emojis": "🔴🔥🌶️🍕", "answer": "red hot chili peppers"},
    "14": {"emojis": "🐝1️⃣👀", "answer": "beyoncé"},
    "15": {"emojis": "🥶🎶", "answer": "coldplay"},
    "16": {"emojis": "🌱📅", "answer": "green day"},
    "17": {"emojis": "🌊🚴‍♂️", "answer": "flo rida"},
    "18": {"emojis": "🌶️👱‍♀️", "answer": "spice girls"},
    "19": {"emojis": "⚫️🩷", "answer": "black pink"},
    "20": {"emojis": "💳🐝", "answer": "cardi b"},
    "21": {"emojis": "🫖📅🔚", "answer": "the weeknd"},
    "22": {"emojis": "🪜🔥", "answer": "stig brenner"},
    "23": {"emojis": "⛓🚬", "answer": "chainsmokers"},
    "24": {"emojis": "🟤🪐", "answer": "bruno mars"},
}

todays_luke = calendar[current_date]

# Function for generating a unique value based on a name
def generate_unique_value_based_on_name(name):
    # Combine the name with a unique value like a UUID
    unique_input = f"{name}-{uuid.uuid4()}"
    
    # Create a hash of the unique input
    unique_hash = hashlib.sha256(unique_input.encode()).hexdigest()
    
    return unique_hash

# Function for registering a user
def register_user(user_name):
    #create unique hash
    user_id = generate_unique_value_based_on_name(user_name)
    
    #Insert into database
    query = execute_query(supabase_client.table("calendar").insert(
            {"user_name": user_name, "cookie_value": user_id}), ttl=0)
    
    #If successful, set cookie
    if query is not None:
        cookie_controller.set(name="user_id", value=user_id, same_site=True, expires=date_obj)
        time.sleep(5) #Sleep for setting cookie
        return True
    else:
        return False  

# Function for getting the data for a user
def get_user(cookie_value):
    user = execute_query(supabase_client.table("calendar").select("*", count="exact").eq("cookie_value", cookie_value), ttl=0)
    user_data = user.data[0] #Data for the user
    todays_data_for_user = user_data[f"day_{current_date}"]  #Data for the current day for a user
    guesses_left = todays_data_for_user["tries"] #How many guesses the user has left
    answer_status = todays_data_for_user["correct"] #If the user has answered correctly or not
    
    return user_data, todays_data_for_user, guesses_left, answer_status

# Function for updating the data for a user
def update_day_data_for_user(cookie_value, data: dict):
    query = execute_query(supabase_client.table("calendar").update(
        {f"day_{current_date}": data}, count="exact").eq("cookie_value", cookie_value), ttl=0)
    return query

# Function for removing whitespace and lowercasing a string
def remove_whitespace_and_lower(s):
    return ''.join(s.split()).lower()

#Classes for html styling
st.markdown(
        """
        <style>
        .centered-title {
            text-align: center;
            color: #ffffff
        }
        
        .info_text {
            color: #ffffff
        }
        
        .info_text_2 {
            font-size: 17px;
            color: #ffffff
            
        }
        
        .emojies{
            text-align: center;
            font-size: 60px;
            letter-spacing: 20px;
        }
        
        .heart-text{
            color: #ffffff;
        }
        
        .hearts{
            letter-spacing: 15px;
        }
        </style>
        """,
        unsafe_allow_html=True)

# Header for site
def header_widget():
        
    st.markdown('<h1 class="centered-title">Julekalender 2024</h1>', unsafe_allow_html=True)
    st.markdown('<h4 class="centered-title">🎅🎄🎁🎉</h4>', unsafe_allow_html=True)
    with st.expander(label="Les mer", expanded=True):
        st.markdown(f'<p class="info_text" >Velkommen til julekalenderen 2024! Hver dag i desember vil du få to emojis. Gjett hvilken musikk artist/gruppe som emojisene representerer! </p>', unsafe_allow_html=True)
        st.markdown(f'<p class="info_text"> Du har tre forsøk per dag på å gjette riktig. Gjetter du feil mister du et liv 😟  </p>', unsafe_allow_html=True)
        st.markdown(f'<p class="info_text"> Lykke til ! </p>', unsafe_allow_html=True)

      
@st.fragment()
def main_widget():
            
    cookie = cookie_controller.get(name="user_id")
     #Cookie logic
    if cookie is None:
        st.markdown(f'<p class="info_text_2"> Ser ut som du er ny her! For å kunne ta del i kalenderen er du nødt til å skrive inn et brukernavn</p>', unsafe_allow_html=True)
        st.markdown(f'<p class="info_text_2"> Prøv å gjør brukernavnet ditt unikt!</p>', unsafe_allow_html=True)
        user_name = st.text_input("For å kunne være med er du nødt til å skrive inn navnet ditt her:", key="name", label_visibility="collapsed")
        if st.button("Bli med i kalenderen") and user_name != "":
            #Regsiter user to database
            with st.spinner('Gjør deg klar...'):
                register_user(user_name)
                st.rerun(scope="fragment")
            
  
    else: 
        #Fetching user data
        user_data, todays_data_for_user, guesses_left, answer_status = get_user(cookie) #Data for the user
        hearts = '🤍' * guesses_left #Hearts to display
        # misses = 'X' * (3 - guesses_left)  # "X" for missed guesses
        # display = hearts + misses  # Combine hearts and misses
        
        st.markdown(f'<h2 class="centered-title">Dagens luke #{current_date}</h2>', unsafe_allow_html=True)
        st.markdown(f'<h1 class="emojies">{todays_luke["emojis"]}</h1>', unsafe_allow_html=True, )
        
        # st.write(answer_status)
        
        if answer_status == True:
            st.markdown('<h4 class="centered-title">Du klarte det! Gratulerer!</h4>', unsafe_allow_html=True)
            st.markdown('<h4 class="centered-title">Kom tilbake i morgen for ny luke 🎅🌲 </h4>', unsafe_allow_html=True)
            return
        
        if guesses_left > 0:
        
            # Add an input field
            st.markdown(f'<h4 class="heart-text">Gjenstående forsøk: <span class="hearts"> {hearts} </span> </h4>', unsafe_allow_html=True)
            user_guess = st.text_input(label="Gjett:", placeholder="Skriv inn ditt svar her", label_visibility="collapsed")
            if st.button("Send inn svar") and user_guess != "":
                
                #If correct
                if remove_whitespace_and_lower(user_guess) == remove_whitespace_and_lower(todays_luke["answer"]): #Cheking the answer
                    update_day_data_for_user(cookie, {"tries": guesses_left - 1, "correct": True})
                    st.rerun(scope="fragment")
                #If wrong
                else:
                    st.session_state.session_answers = False
                    update_day_data_for_user(cookie, {"tries": guesses_left - 1, "correct": False})
                    st.rerun(scope="fragment")
              
        else:
            if answer_status == True:
                st.markdown('<h4 class="centered-title">Du klarte det! Gratulerer</h4>', unsafe_allow_html=True)
                st.markdown('<h4 class="centered-title">Kom tilbake i morgen for ny luke 🎅🌲 </h4>', unsafe_allow_html=True)
            else:
                st.markdown('<h4 class="centered-title">Beklager! Du klarte det dessverre ikke</h4>', unsafe_allow_html=True)
                st.markdown('<h4 class="centered-title">Kom tilbake i morgen for ny luke 🎅🌲 </h4>', unsafe_allow_html=True)
    

    
    

def main():
    cookie = cookie_controller.get(name="user_id")
    st.session_state.session_answers = None

    if int(current_month) != 12:
        st.markdown('<h1 class="centered-title">Julekalenderen er kun tilgjengelig i desember! 🎄</h1>', unsafe_allow_html=True)
        return
    
    elif current_month == 12 and int(current_date) > 24:
        st.markdown('<h1 class="centered-title">Julekalenderen er ferdig for i år!</h1>', unsafe_allow_html=True)
        st.markdown('<h2 class="centered-title">Vi vil publisere et leaderboard så fort vi er klare 🎅</h2>', unsafe_allow_html=True)
        st.markdown('<h2 class="centered-title">Gooood jul</h2>', unsafe_allow_html=True)
        return
    
    header_widget()
    
    main_widget()
    

        
            
    # def add_footer():
    #     footer = """
    #     <style>
    #     .footer {
    #         position: fixed;
    #         left: 0;
    #         bottom: 0;
    #         width: 100%;
    #         # background-color: black;
    #         color: white;
    #         text-align: center;
    #         padding: 10px 0;
    #     }
    #     </style>
    #     <div class="footer">
    #         Developed by Thomas with love ❤️
    #     </div>
    #     """
    #     st.markdown(footer, unsafe_allow_html=True)
    
    # add_footer()
    
    
if __name__ == '__main__':
    main()
