import logging
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, flash, g
from flask_babel import Babel, gettext as _
from config import Config

# --- Application Setup ---
app = Flask(__name__)
app.config.from_object(Config)


def get_locale():
    # 1. Check if a language is stored in the session
    if 'language' in session and session['language'] in app.config['LANGUAGES']:
        return session['language']
    # 2. Otherwise, try to use the browser's preferred language
    return request.accept_languages.best_match(app.config['LANGUAGES'])


# --- Internationalization (i18n) Setup ---
babel = Babel(app, locale_selector=get_locale)


# Make the current language available in all templates
@app.before_request
def before_request():
    g.locale = str(get_locale())
    if 'logged_in' not in session:
        session['logged_in'] = False

# --- Visitor Logging Setup ---
# Set up a specific logger for visits
visit_logger = logging.getLogger('visit_logger')
visit_logger.setLevel(logging.INFO)
handler = logging.FileHandler('visits.log')
formatter = logging.Formatter('%(asctime)s - %(message)s')
handler.setFormatter(formatter)
visit_logger.addHandler(handler)


# --- Routes ---

@app.route('/language/<lang>')
def set_language(lang=None):
    if lang in app.config['LANGUAGES']:
        session['language'] = lang
    # Redirect back to the page the user was on
    return redirect(request.referrer or url_for('index'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if session.get('logged_in'):
        return redirect(url_for('index'))

    if request.method == 'POST':
        entered_code = request.form.get('code')
        if entered_code == app.config['EVENT_ACCESS_CODE']:
            session['logged_in'] = True
            
            # Log the successful visit
            ip_address = request.remote_addr
            user_agent = request.headers.get('User-Agent')
            visit_logger.info(f"Successful login from IP: {ip_address}, User-Agent: {user_agent}")
            
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
            "question": _("At what time should I be there?"),
            "answer": _("We are planning to start our celebration at 15 h (3 pm), so make you sure you don't miss a bit!")
        },
        {
            "question": _("I'm not sure what to wear..."),
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
        }

    ]
    return render_template('faq.html', faq_items=faq_items)

@app.route('/map')
@login_required
def map_page():
    return render_template('map.html')

@app.route('/rvsp')
@login_required
def rvsp_func():
    return render_template('rvsp.html')


if __name__ == '__main__':
    # This is for local development only.
    # For production, use a proper WSGI server like Gunicorn or uWSGI.
    app.run()
