from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from . import db

from .models import User, Route, RouteStop, Ticket, QualityOfService, Station, Session

admin = Blueprint('admin', __name__)

MODELS = {
    "User": User,
    "Route": Route,
    "TrainStop": RouteStop,
    "Ticket": Ticket,
    "QualityOfService": QualityOfService,
    "Station": Station,

    "Session": Session
}

@admin.route('/', methods=['GET', 'POST'])
def admin_panel():
    if request.method == 'POST':
        model_name = request.form.get('model')
        return redirect(url_for('admin.manage_model', model_name=model_name))
    return render_template('admin_panel.html', models=MODELS.keys())

@admin.route('/admin/<model_name>', methods=['GET', 'POST'])
def manage_model(model_name):
    model_class = MODELS.get(model_name)
    if not model_class:
        flash("Invalid model selected", "danger")
        return redirect(url_for('admin.admin_panel'))

    if request.method == 'POST':
        data = {key: request.form[key] for key in request.form}
        try:
            new_entry = model_class(**data)
            db.session.add(new_entry)
            db.session.commit()
            flash(f"{model_name} entry added successfully!", "success")
        except Exception as e:
            flash(f"Error: {str(e)}", "danger")
        return redirect(url_for('admin.manage_model', model_name=model_name))

    entries = model_class.query.all()
    columns = [col.name for col in model_class.__table__.columns]

    return render_template(
        'manage_model.html',
        model_name=model_name,
        entries=entries,
        columns=columns,
        getattr=getattr
    )

@admin.route('/<model_name>/delete/<int:entry_id>', methods=['POST'])
def delete_entry(model_name, entry_id):
    model_class = MODELS.get(model_name)
    if not model_class:
        flash("Invalid model selected", "danger")
        return redirect('/admin')

    try:
        entry = model_class.query.get(entry_id)
        if entry:
            db.session.delete(entry)
            db.session.commit()
            flash(f"Entry deleted successfully!", "success")
        else:
            flash("Entry not found.", "warning")
    except Exception as e:
        flash(f"Error: {str(e)}", "danger")
    
    return redirect(url_for('admin.manage_model', model_name=model_name))
