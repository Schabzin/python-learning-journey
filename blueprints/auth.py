from flask import Blueprint, request, session, redirect, url_for, flash, render_template
from extensions import get_db
import bcrypt

auth = Blueprint("auth")