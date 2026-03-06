import logging
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session, flash, g, Response
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_babel import Babel, gettext as _
from config import Config

# --- Application Setup ---
app = Flask(__name__)
app.config.from_object(Config)
limiter = Limiter(app, key_func=get_remote_address)
# --- Internationalization (i18n) Setup ---
babel = Babel(app, locale_selector=get_locale)


def get_locale():
    # 1. Check if a language is stored in the session
    if 'language' in session and session['language'] in app.config['LANGUAGES']:
        return session['language']
    # 2. Otherwise, try to use the browser's preferred language
    return request.accept_languages.best_match(app.config['LANGUAGES'])


# Make the current language available in all templates
@app.before_request
def before_request():
    g.locale = str(get_locale())
    if 'logged_in' not in session:
        session['logged_in'] = False


# --- DB ---

def init_db():
    conn = sqlite3.connect(app.config['DB_LOCATION']) #if DB doesn´t exist -> creates it; if does exist - connects to the DB
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS guests (
            name TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


# --- Routes ---

@app.route('/language/<lang>')
def set_language(lang=None):
    if lang in app.config['LANGUAGES']:
        session['language'] = lang
    # Redirect back to the page the user was on
    return redirect(request.referrer or url_for('index'))

@app.route('/login', methods=['GET', 'POST'])
@limiter.limit("15 per minute")
def login():
    if session.get('logged_in'):
        return redirect(url_for('index'))

    if request.method == 'POST':
        entered_code = request.form.get('code')
        if entered_code == app.config['EVENT_ACCESS_CODE']:
            session['logged_in'] = True
            
            return redirect(url_for('index'))
        else:
            # The _() function marks the string for translation
            flash(_('Invalid access code. Please try again.'), 'error')
            
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash(_('You have been logged out.'), 'info')
    return redirect(url_for('login'))

# This function checks if the user is logged in before accessing protected pages
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    # The next line is needed to avoid an error with Flask routing
    decorated_function.__name__ = f.__name__
    return decorated_function

@app.route('/')
@login_required
def index():
    return render_template('index.html')


@app.route('/faq')
@login_required
def faq():
    # Example of passing dynamic data to the template
    faq_items = [
        {
            "question": _("Where will be the event?"),
            "answer": _("Our celebration will take place in the grounds and buildings surrounding Casa de Hóspedes da Tapada de Mafra.")
        },

        {
            "question": _("What should I expect during the day?"),
            "answer": _("The first part of our celebration will be led outdoors, in the garden and surroundings of Casa de Hóspedes da Tapada. We intend to make the most of all the nature that Tapada has to offer, so keep your eyes peeled - if you are lucky, you may catch a glimpse of some of the wildlife...! We are planning on having some traditional games during the afternoon, so, please bring along your good humor and fair play! During the evening, we will procede to the main pavillion, in order to enjoy a little bit of dancing!")
        },
        {
            "question": _("At what time should I be there?"),
            "answer": _("We are planning to start our celebration at 15 h (3 pm), so make you sure you don't miss a bit!")
        },
        {
            "question": _("I'm not sure what to wear, if you're going to make me run around..."),
            "answer": _("The dress code is \"They're taking the hobbits to Isengard! 🧙🏻‍♂  🧝‍♂ \"! (Kidding… unless you were already planning the staff and cloak!) In all seriousness, think smart casual. We’re hoping the day feels more like a relaxed gathering of friends — a garden party with plenty of games, food and laughter — rather than a very formal affair. That said, feel free to dress up if you’re in the mood… just kindly leave the white to the bride. 😉 \n\n P.S.: WE STRONGLY ADVISE YOU TO BRING YOUR SNEAKERS ALONG!")
        },
        {
            "question": _("Is there parking available?"),
            "answer": _("Yes, free parking is available at the venue's main parking lot.")
        },
        {
            "question": _("Can I bring a plus-one?"),
            "answer": _("Please check your invitation. This event is invite-only, unless explicitly said otherwise.")
        },
        {
            "question": _("By when should I let you know if I’ll be attending?"),
            "answer": _("Please, give us your answer by 31/03/2026.")
        },
        {
            "question": _("How should I let you know if I’ll be attending?"),
            "answer": _("In true organised fashion, we’ve prepared a lovely little form in the CONFIRMAR PRESENÇA/RVSP section, for you to fill out with the name(s) of the attending guest(s). ")
        },
        {
            "question": _("Are kids welcome?"),
            "answer": _("Children are welcome, but, please, remember to add their names to the RSVP form so we can include them in our final headcount.")
        },
        {
            "question": _("OMG, I see a deer, may I go pet him?"),
            "answer": _("Please, bear in mind that Tapada is a wildlife reserve - while the animals may be used to human visitors, they remain wild. For their safety and yours, we kindly ask that you do not approach or feed them.")
        },
        {
            "question": _("I have a question that's not answered in the FAQ section..."),
            "answer": _("In case you have extra questions, feel free to reach our costumer service by phone at 00351917200606 or 00351961115694 (phone calls, SMS or whatsapp), Mon-Fri from 8 a.m.to 8 p.m.")
        }

    ]
    return render_template('faq.html', faq_items=faq_items)

@app.route('/map')
@login_required
def map_page():
    return render_template('map.html')

@app.route("/rvsp", methods=["GET", "POST"])
@login_required
def rvsp():
    if request.method == "POST":
        names = request.form.getlist("name")

        if not names:
            flash(_('Please add at least one guest.'))
            return redirect(url_for('rvsp'))

        conn = sqlite3.connect(app.config['DB_LOCATION'])
        cursor = conn.cursor()

        for name in names:
            name = name.strip()

            if len(name) > 40:
                # flash(_('Name must be 40 characters or fewer.')) # Not being used
                conn.close()
                return redirect(url_for('rvsp'))

            if name:
                cursor.execute("INSERT INTO guests (name) VALUES (?)", (name,))

        conn.commit()
        conn.close()

        return redirect(url_for("thank_you"))

    return render_template("rvsp.html")


@app.route("/thank-you")
@login_required
def thank_you():
    return render_template('thankyou.html')



#---------------------
with app.app_context():
    init_db()


if __name__ == '__main__':
    # for local development only.
    # For production, use a proper WSGI server like Gunicorn or uWSGI.
    app.run()
