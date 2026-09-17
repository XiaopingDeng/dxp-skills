# Shipping to GitHub Pages

Detail for Step 7. Write the `README.md` deployment section from this recipe — the user will follow
it later, without you.

## Default to HTTPS + token, not SSH

SSH is the flow that most often dead-ends: a fresh Windows box has an `id_rsa` that was never
registered with GitHub, so `git push` dies with `Permission denied (publickey)` and the user has no
idea why. Write the deployment section as a numbered recipe:

1. **Create the repo in the web UI** at `https://github.com/new` — name exactly
   `<username>.github.io`, visibility **Public** (Pages on a private repo needs a paid plan), and
   **do not** tick README / `.gitignore` / license. A pre-seeded repo turns the first `git push` into
   a `! [rejected] ... (fetch first)` conflict that beginners can't untangle.
2. **Generate a classic token** at `https://github.com/settings/tokens` → *Generate new token
   (classic)*, scope **`repo`** (the whole block). Say plainly that it is shown once — copy it now.
3. **Point the remote at HTTPS and push.**
   ```bash
   git remote set-url origin https://github.com/<username>/<username>.github.io.git
   git remote -v          # verify the https:// form
   git push -u origin main
   ```
   Then a credentials table, because this is where people trip: **Username** = the GitHub username;
   **Password** = paste the `ghp_…` token, *not* the account password.
4. **Turn Pages on**: Settings → Pages → *Deploy from a branch* → `main` + `/ (root)` → Save.
   A fresh repo does not serve by default, so this step is not optional — until it is done the root
   URL 404s even though the push succeeded.

## Before writing the instructions

- **The repo name must be exactly `<username>.github.io`, case included.** Read the real username off
  a link the user already gave you (e.g. their GitHub profile URL) — never guess it from the pinyin of
  their name. `JaneDoe` ≠ `janedoe`, and a case-mismatched repo silently 404s at the root URL.
- Check `git config --global credential.helper`. If it is empty the first push prompts for
  credentials interactively — harmless, but say so rather than letting the user think it hung.
- `gh` CLI is often absent, so don't build the recipe around `gh repo create`.
- **Verify the result, don't assume it.** Fetch the root URL, `/en.html` and `/styles.css` after
  handing over; a 404 on all three means Pages is off (or still building), not that the push failed.

## Symptom → cause → fix

The five that actually happen:

| Symptom | Cause | Fix |
|---|---|---|
| `git push` → `Permission denied (publickey)` | SSH remote whose key was never registered on that GitHub account | `git remote set-url origin https://github.com/<user>/<user>.github.io.git` |
| `repository not found` | the repo was never created, or the name/case doesn't match | create it in the web UI; re-read the real username |
| `Support for password authentication was removed` | the account password was typed instead of the token | use the `ghp_…` token as the password |
| `rejected ... (fetch first)` | README / `.gitignore` / license was ticked at creation | `git pull --rebase origin main`, then push |
| The root URL 404s | either the repo isn't `<username>.github.io`, or Pages was never switched on | fix the name; then Settings → Pages → *Deploy from a branch* → `main` / `(root)` |
