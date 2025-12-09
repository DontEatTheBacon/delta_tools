import sqlalchemy as sa
from flask import flash, redirect, render_template, url_for
from flask_login import current_user, login_required, login_user, logout_user

import delta_api
from app import db
from app.main import bp
from app.main.forms import LoginForm, RegistrationForm, CourseSearchForm
from app.models import User

@bp.route('/')
@bp.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    form = CourseSearchForm()
    if form.validate_on_submit():
        courses = delta_api.search_course(form.query.data, 100)
        return render_template('index.html', courses=courses, form=form)
    return render_template('index.html', form=form)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.scalar(sa.select(User).where(User.username == form.username.data))
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('main.login'))
        login_user(user, remember=form.remember_me.data)
        flash('Successfully logged in as {}'.format(form.username.data))
        return redirect(url_for('main.index'))
    return render_template('login.html', form=form)

@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Successfully registerd {}!'.format(user.username))
        return redirect(url_for('main.index'))

    return render_template('register.html', form=form)

@bp.route('/courses/<course_id>')
def courses(course_id):
    sections = delta_api.get_sections(course_id)
    return render_template('sections.html', sections=sections, section_name=sections[0].course_name if sections else 'Unknown Course')

@bp.route('/courses/<course_id>/sections/<section_id>')
def sections(course_id, section_id):
    section = delta_api.get_section(course_id, section_id)
    return render_template('class.html', section=section)
