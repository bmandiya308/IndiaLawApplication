import os
import sqlite3
from contextlib import closing

from flask import Flask, abort, flash, g, jsonify, redirect, render_template, request, url_for


BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.path.join(BASE_DIR, "instance", "ipc.db")

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "ipc-catalog-development-key")
app.config["DATABASE"] = DATABASE


SEED_ARTICLES = [
    ("1", "Title and extent of operation", "General Explanations", "This Act shall be called the Indian Penal Code and extends to the whole of India.", "The section defines the name and territorial reach of the Code."),
    ("34", "Acts done by several persons in furtherance of common intention", "General Exceptions", "When a criminal act is done by several persons in furtherance of the common intention of all, each person is liable for that act in the same manner as if it were done by that person alone.", "Common intention requires participation in the criminal act and a shared intention. The facts and evidence determine whether the provision applies."),
    ("107", "Abetment of a thing", "Of Abetment", "A person abets the doing of a thing when the person instigates another, engages in a conspiracy, or intentionally aids the doing of that thing.", "The section describes the three forms of abetment: instigation, conspiracy with an act or illegal omission, and intentional aid."),
    ("120B", "Punishment of criminal conspiracy", "Of Criminal Conspiracy", "Whoever is a party to a criminal conspiracy shall be punished in the manner provided by this section.", "The punishment depends on the object of the conspiracy and the applicable offence."),
    ("141", "Unlawful assembly", "Of Offences Against the Public Tranquillity", "An assembly of five or more persons is designated an unlawful assembly if its common object falls within any of the objects described in this section.", "The common object and the conduct of the assembly are central to applying this provision."),
    ("146", "Rioting", "Of Offences Against the Public Tranquillity", "Whenever force or violence is used by an unlawful assembly, or by any member thereof, in prosecution of the common object of such assembly, every member is guilty of rioting.", "Rioting builds on unlawful assembly and requires force or violence used in pursuit of the common object."),
    ("153A", "Promoting enmity between different groups", "Of Offences Against the Public Tranquillity", "Whoever promotes or attempts to promote, on grounds such as religion, race, place of birth or residence, disharmony or feelings of enmity between different groups is punishable under this section.", "The provision addresses conduct that threatens communal harmony. Read the statutory text and current amendments together."),
    ("186", "Obstructing public servant in discharge of public functions", "Of Contempts of the Lawful Authority of Public Servants", "Whoever voluntarily obstructs any public servant in the discharge of public functions is punishable under this section.", "The prosecution must establish voluntary obstruction and the public servant's lawful public function."),
    ("302", "Punishment for murder", "Of Offences Affecting the Human Body", "Whoever commits murder shall be punished with death, or imprisonment for life, and shall also be liable to fine.", "This is a punishment provision. Whether conduct amounts to murder depends on the ingredients and exceptions in the Code."),
    ("304A", "Causing death by negligence", "Of Offences Affecting the Human Body", "Whoever causes the death of any person by doing any rash or negligent act not amounting to culpable homicide is punishable under this section.", "The section concerns rash or negligent acts causing death where the facts do not amount to culpable homicide."),
    ("307", "Attempt to murder", "Of Offences Affecting the Human Body", "Whoever does any act with such intention or knowledge, and under such circumstances that, if the act caused death, the person would be guilty of murder, is punishable under this section.", "The intention or knowledge and the act done are examined together to determine whether the offence is made out."),
    ("323", "Punishment for voluntarily causing hurt", "Of Offences Affecting the Human Body", "Whoever, except in the case provided for by section 334, voluntarily causes hurt, shall be punished under this section.", "This is the general punishment provision for voluntarily causing hurt, subject to the exceptions and related provisions."),
    ("354", "Assault or criminal force to woman with intent to outrage her modesty", "Of Assault", "Whoever assaults or uses criminal force to any woman, intending to outrage or knowing it to be likely that the person's act will outrage her modesty, is punishable under this section.", "The intent or knowledge and the assault or criminal force are important elements of the offence."),
    ("375", "Rape", "Of Sexual Offences", "A man is said to commit rape when he has sexual intercourse with a woman in circumstances falling within the descriptions in this section.", "The statutory definition contains specific circumstances and exceptions. Consult the current law and amendments before relying on this entry."),
    ("376", "Punishment for rape", "Of Sexual Offences", "Whoever commits rape, except in certain circumstances covered by the section, shall be punished as provided here.", "This is a punishment provision and has been amended over time. Always verify the current text and applicable special statutes."),
    ("379", "Punishment for theft", "Of Offences Against Property", "Whoever commits theft shall be punished under this section.", "Theft is defined in section 378. This section provides its general punishment."),
    ("392", "Punishment for robbery", "Of Robbery and Dacoity", "Whoever commits robbery shall be punished under this section.", "Robbery incorporates theft or extortion with the additional circumstances described in the Code."),
    ("406", "Punishment for criminal breach of trust", "Of Criminal Breach of Contracts of Service", "Whoever commits criminal breach of trust shall be punished under this section.", "The offence depends on entrustment or dominion over property and dishonest use or disposal contrary to the required legal duty."),
    ("420", "Cheating and dishonestly inducing delivery of property", "Of Cheating", "Whoever cheats and thereby dishonestly induces the person deceived to deliver property or to make, alter or destroy a valuable security is punishable under this section.", "Deception, dishonest inducement, and delivery or alteration of property or security are the central ingredients."),
    ("498A", "Husband or relative of husband subjecting woman to cruelty", "Of Cruelty by Husband or Relatives of Husband", "Whoever, being the husband or the relative of the husband of a woman, subjects her to cruelty is punishable under this section.", "Cruelty includes the conduct and dowry-related circumstances described in the statutory explanation."),
    ("499", "Defamation", "Of Defamation", "Whoever, by words spoken or intended to be read, or by signs or visible representations, makes or publishes an imputation concerning any person intending to harm, or knowing or having reason to believe that it will harm, that person's reputation, commits defamation.", "The section includes explanations and exceptions that must be read with the definition."),
    ("500", "Punishment for defamation", "Of Defamation", "Whoever defames another shall be punished under this section.", "This section provides the general punishment for defamation defined in section 499."),
    ("506", "Punishment for criminal intimidation", "Of Criminal Intimidation, Insult and Annoyance", "Whoever commits the offence of criminal intimidation shall be punished under this section.", "Criminal intimidation is defined in section 503 and concerns threats intended to cause alarm or compel conduct."),
    ("509", "Word, gesture or act intended to insult modesty of a woman", "Of Criminal Intimidation, Insult and Annoyance", "Whoever, intending to insult the modesty of any woman, utters a word, makes a sound or gesture, exhibits an object, or intrudes upon her privacy is punishable under this section.", "The intention and the nature of the word, gesture, act, or intrusion are material."),
]

PUNISHMENTS = {
    "1": "Not a punishment provision; this section states the name and extent of the Code.",
    "34": "No separate punishment is prescribed here. Each participant may be liable for the criminal act as if they had done it alone.",
    "107": "Abetment is punished under the provision applicable to the abetted offence, including section 109 where applicable.",
    "120B": "Punishment depends on the offence that is the object of the conspiracy; the section provides different treatment for serious offences and other conspiracies.",
    "141": "Not a punishment provision; unlawful assembly is defined here. The related punishment for membership is generally provided by section 143.",
    "146": "The related punishment for rioting is generally imprisonment up to two years, or fine, or both under section 147.",
    "153A": "Imprisonment up to three years, or fine, or both; offences in a place of worship may attract imprisonment up to five years and fine.",
    "186": "Imprisonment up to three months, or fine up to 500 rupees, or both.",
    "302": "Death or imprisonment for life, and liability to fine.",
    "304A": "Imprisonment up to two years, or fine, or both.",
    "307": "Imprisonment up to ten years and fine; if hurt is caused, imprisonment for life or the stated imprisonment and fine may apply.",
    "323": "Imprisonment up to one year, or fine up to 1,000 rupees, or both.",
    "354": "Imprisonment of either description for at least one year and up to five years, and fine.",
    "375": "Not a punishment provision; this section defines rape. Punishment is provided by section 376 and related provisions.",
    "376": "Generally rigorous imprisonment of at least ten years and up to imprisonment for life, and fine, subject to the applicable circumstances and amendments.",
    "379": "Imprisonment up to three years, or fine, or both.",
    "392": "Rigorous imprisonment up to ten years and fine; robbery on a highway between sunset and sunrise may attract imprisonment up to fourteen years.",
    "406": "Imprisonment up to three years, or fine, or both.",
    "420": "Imprisonment up to seven years and fine.",
    "498A": "Imprisonment up to three years and fine.",
    "499": "Not a punishment provision; this section defines defamation. Punishment is provided by section 500.",
    "500": "Simple imprisonment up to two years, or fine, or both.",
    "506": "Imprisonment up to two years, or fine, or both; aggravated threats may attract imprisonment up to seven years, or fine, or both.",
    "509": "Simple imprisonment up to three years and fine.",
}
DEFAULT_PUNISHMENT = "Verify the current statutory punishment, applicable exceptions, and amendments before relying on this entry."


def get_db():
    if "db" not in g:
        os.makedirs(os.path.dirname(app.config["DATABASE"]), exist_ok=True)
        g.db = sqlite3.connect(app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(_error=None):
    database = g.pop("db", None)
    if database is not None:
        database.close()


def init_db():
    database = get_db()
    database.execute(
        """CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            section_code TEXT NOT NULL UNIQUE,
            title TEXT NOT NULL,
            chapter TEXT NOT NULL,
            text TEXT NOT NULL,
            details TEXT NOT NULL,
            punishment TEXT NOT NULL DEFAULT '""',
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )"""
    )
    columns = {row[1] for row in database.execute("PRAGMA table_info(articles)").fetchall()}
    if "punishment" not in columns:
        database.execute("ALTER TABLE articles ADD COLUMN punishment TEXT NOT NULL DEFAULT ''")
    count = database.execute("SELECT COUNT(*) FROM articles").fetchone()[0]
    if count == 0:
        database.executemany(
            "INSERT INTO articles (section_code, title, chapter, text, details, punishment) VALUES (?, ?, ?, ?, ?, ?)",
            [article + (PUNISHMENTS.get(article[0], DEFAULT_PUNISHMENT),) for article in SEED_ARTICLES],
        )
    else:
        for section_code, punishment in PUNISHMENTS.items():
            database.execute(
                "UPDATE articles SET punishment = ? WHERE section_code = ? AND (punishment = '' OR punishment IS NULL)",
                (punishment, section_code),
            )
    database.commit()


def article_from_form(form):
    values = {
        "section_code": form.get("section_code", "").strip(),
        "title": form.get("title", "").strip(),
        "chapter": form.get("chapter", "").strip(),
        "text": form.get("text", "").strip(),
        "details": form.get("details", "").strip(),
        "punishment": form.get("punishment", "").strip(),
    }
    missing = [field for field, value in values.items() if not value]
    return values, missing


@app.context_processor
def inject_catalog_stats():
    total = get_db().execute("SELECT COUNT(*) FROM articles").fetchone()[0]
    chapters = get_db().execute("SELECT COUNT(DISTINCT chapter) FROM articles").fetchone()[0]
    return {"article_count": total, "chapter_count": chapters}


@app.route("/")
def index():
    query = request.args.get("q", "").strip()
    chapter = request.args.get("chapter", "").strip()
    database = get_db()
    sql = "SELECT * FROM articles WHERE 1 = 1"
    params = []
    if query:
        sql += " AND (section_code LIKE ? OR title LIKE ? OR chapter LIKE ? OR text LIKE ? OR details LIKE ?)"
        params.extend([f"%{query}%"] * 5)
    if chapter:
        sql += " AND chapter = ?"
        params.append(chapter)
    sql += " ORDER BY CAST(section_code AS INTEGER), section_code"
    articles = database.execute(sql, params).fetchall()
    chapters = database.execute("SELECT DISTINCT chapter FROM articles ORDER BY chapter").fetchall()
    return render_template("index.html", articles=articles, chapters=chapters, query=query, selected_chapter=chapter)


@app.route("/article/<int:article_id>")
def article_detail(article_id):
    article = get_db().execute("SELECT * FROM articles WHERE id = ?", (article_id,)).fetchone()
    if article is None:
        abort(404)
    return render_template("article.html", article=article)


@app.route("/add", methods=["GET", "POST"])
def add_article():
    if request.method == "POST":
        values, missing = article_from_form(request.form)
        if missing:
            flash("Please complete all fields before saving the article.", "error")
            return render_template("add.html", values=values), 400
        try:
            database = get_db()
            cursor = database.execute(
                "INSERT INTO articles (section_code, title, chapter, text, details, punishment) VALUES (?, ?, ?, ?, ?, ?)",
                tuple(values.values()),
            )
            database.commit()
        except sqlite3.IntegrityError:
            flash("That IPC section already exists in the catalog.", "error")
            return render_template("add.html", values=values), 409
        flash("Article added to the IPC catalog.", "success")
        return redirect(url_for("article_detail", article_id=cursor.lastrowid))
    return render_template("add.html", values={})


@app.route("/api/articles", methods=["GET", "POST"])
def articles_api():
    database = get_db()
    if request.method == "GET":
        query = request.args.get("q", "").strip()
        if query:
            rows = database.execute(
                "SELECT * FROM articles WHERE section_code LIKE ? OR title LIKE ? OR chapter LIKE ? ORDER BY section_code",
                tuple([f"%{query}%"] * 3),
            ).fetchall()
        else:
            rows = database.execute("SELECT * FROM articles ORDER BY CAST(section_code AS INTEGER), section_code").fetchall()
        return jsonify([dict(row) for row in rows])

    payload = request.get_json(silent=True) or {}
    values, missing = article_from_form(payload)
    if missing:
        return jsonify({"message": "All fields are required", "missing": missing}), 400
    try:
        cursor = database.execute(
            "INSERT INTO articles (section_code, title, chapter, text, details, punishment) VALUES (?, ?, ?, ?, ?, ?)",
            tuple(values.values()),
        )
        database.commit()
    except sqlite3.IntegrityError:
        return jsonify({"message": "That IPC section already exists"}), 409
    row = database.execute("SELECT * FROM articles WHERE id = ?", (cursor.lastrowid,)).fetchone()
    return jsonify(dict(row)), 201


@app.errorhandler(404)
def not_found(error):
    if request.path.startswith("/api/"):
        return jsonify({"message": "Article not found"}), 404
    return render_template("404.html"), 404


with app.app_context():
    init_db()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)