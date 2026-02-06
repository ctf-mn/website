import os
import secrets
from time import time
from urllib.parse import urlencode

import requests
from flask import Blueprint, flash, g, redirect, request, session

import models as db

bp = Blueprint('discord', __name__)

DISCORD_AUTH_URL = 'https://discord.com/oauth2/authorize'
DISCORD_TOKEN_URL = 'https://discord.com/api/v10/oauth2/token'
DISCORD_USER_URL = 'https://discord.com/api/v10/users/@me'

DISCORD_CLIENT_ID = os.environ['DISCORD_CLIENT_ID']
DISCORD_CLIENT_SECRET = os.environ['DISCORD_CLIENT_SECRET']


class DiscordOAuthError(Exception):
    """Base exception for Discord OAuth errors."""


class DiscordOAuthCancelled(DiscordOAuthError):
    """Raised when the user cancels the OAuth flow."""


class DiscordOAuthFailed(DiscordOAuthError):
    """Raised when the OAuth flow fails."""


def get_discord_user_id(state_key: str, redirect_uri: str) -> str:
    """
    Validate OAuth callback and retrieve Discord user ID.

    Args:
        state_key: Session key where the state token is stored.
        redirect_uri: The redirect URI used in the OAuth flow.

    Returns:
        The Discord user ID.

    Raises:
        DiscordOAuthCancelled: If the user cancelled the OAuth flow.
        DiscordOAuthFailed: If the OAuth flow failed.
    """
    stored_state = session.pop(state_key, None)
    if not stored_state or stored_state != request.args.get('state'):
        raise DiscordOAuthFailed()
    if request.args.get('error'):
        raise DiscordOAuthCancelled()
    code = request.args.get('code')
    if not code:
        raise DiscordOAuthFailed()

    token_data = {
        'client_id': DISCORD_CLIENT_ID,
        'client_secret': DISCORD_CLIENT_SECRET,
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': redirect_uri,
    }
    token_response = requests.post(DISCORD_TOKEN_URL, data=token_data)
    if token_response.status_code != 200:
        raise DiscordOAuthFailed()
    access_token = token_response.json().get('access_token')
    if not access_token:
        raise DiscordOAuthFailed()

    headers = {'Authorization': f'Bearer {access_token}'}
    user_response = requests.get(DISCORD_USER_URL, headers=headers)
    if user_response.status_code != 200:
        raise DiscordOAuthFailed()

    discord_user = user_response.json()
    discord_user_id = discord_user.get('id')
    if not discord_user_id:
        raise DiscordOAuthFailed()
    return discord_user_id


@bp.route('/link/discord')
def link_discord():
    if not g.user:
        return redirect('/login')
    if g.user.discord_user_id:
        flash('You have already linked a Discord account!', 'error')
        return redirect('/')

    state = secrets.token_urlsafe(32)
    session['discord_oauth_state'] = state

    redirect_uri = request.host_url + 'link/discord/callback'
    params = {
        'client_id': DISCORD_CLIENT_ID,
        'redirect_uri': redirect_uri,
        'response_type': 'code',
        'scope': 'identify',
        'state': state,
    }
    return redirect(f'{DISCORD_AUTH_URL}?{urlencode(params)}')


@bp.route('/link/discord/callback')
def link_discord_callback():
    if not g.user:
        return redirect('/login')
    if g.user.discord_user_id:
        flash('You have already linked a Discord account!', 'error')
        return redirect('/')

    try:
        redirect_uri = request.host_url + 'link/discord/callback'
        discord_user_id = get_discord_user_id('discord_oauth_state', redirect_uri)
    except DiscordOAuthCancelled:
        flash('Discord linking was cancelled.', 'error')
        return redirect('/')
    except DiscordOAuthFailed:
        flash('Failed to link a Discord account. Please try again.', 'error')
        return redirect('/')

    existing_user = db.User.get_or_none(db.User.discord_user_id == discord_user_id)
    if existing_user and existing_user.id != g.user.id:
        flash('This Discord account is already associated with other user!', 'error')
        return redirect('/')

    g.user.discord_user_id = discord_user_id
    g.user.save()

    flash('Linked a Discord account successfully!', 'success')
    return redirect('/')


@bp.route('/auth/discord')
def auth_discord():
    if g.user:
        return redirect('/')

    state = secrets.token_urlsafe(32)
    session['discord_auth_state'] = state

    redirect_uri = request.host_url + 'auth/discord/callback'
    params = {
        'client_id': DISCORD_CLIENT_ID,
        'redirect_uri': redirect_uri,
        'response_type': 'code',
        'scope': 'identify',
        'state': state,
    }
    return redirect(f'{DISCORD_AUTH_URL}?{urlencode(params)}')


@bp.route('/auth/discord/callback')
def auth_discord_callback():
    if g.user:
        return redirect('/')

    try:
        redirect_uri = request.host_url + 'auth/discord/callback'
        discord_user_id = get_discord_user_id('discord_auth_state', redirect_uri)
    except DiscordOAuthCancelled:
        flash('Discord sign-in was cancelled.', 'error')
        return redirect('/login')
    except DiscordOAuthFailed:
        flash('Failed to sign in with Discord. Please try again.', 'error')
        return redirect('/login')

    user = db.User.get_or_none(db.User.discord_user_id == discord_user_id)
    if not user:
        flash('No user found linked to this Discord account. Please register and link your Discord first.', 'error')
        return redirect('/login')

    session['user'] = {
        'email': user.email,
        'logged_in': int(time()),
    }
    return redirect('/')
