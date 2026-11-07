# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

Lavannya Daigavane's personal site, live at **https://lavannya.me**. Hand-written static HTML: no build step, no package manager, no framework, no tests, no linter.

## Commands

```bash
# preview locally (then open http://localhost:8000/blog8.html etc.)
python -m http.server 8000

# check every local link and image resolves (run before committing)
python -c "import re,glob,os;[print(p,'->',r) for p in glob.glob('*.html') for r in set(re.findall(r'(?:src|href)=\"((?:images/)?[^\"/:#?]+\.(?:html|jpe?g|png|css))\"',open(p,encoding='utf-8').read())) if not os.path.exists(r)]"
```

## Deploying

Pushing `main` to GitHub (`github.com/lavannyadaigavane/website`) triggers **Netlify**, which publishes to lavannya.me in about a minute. GitHub Pages is not used, so ignore `has_pages: false`.

- A push publishes straight to the live site. **Confirm with the user before `git push`**, and never force-push.
- If a push fails with "Invalid username or token", the saved GitHub login has expired. The user has to remove `git:https://github.com` from Windows Credential Manager and run `git push` once themselves to sign in through the browser.
- Branch `local-backup-2026-11-07` holds the folder's state from before it was synced with GitHub, including the unlinked drafts `blog5`–`blog7.html`. Leave it alone unless asked.
- Python 3.10 on this machine has an outdated CA bundle, so `urllib` fails TLS against lavannya.me. Use `curl` to check the live site.

## Architecture

**Every page is self-contained.** Each `.html` file carries its own `<style>`, `<script>` and Google Fonts link. Nothing is shared at build time. Changing the look of one page never affects another, and a fix to a shared pattern (nav, like button) has to be repeated in each file.

Pages fall into three design families. Match the family you're editing:

| Family | Fonts | Pages |
|---|---|---|
| **Paper scrapbook**: cream graph-paper ground, taped sheets, wax seal, handwriting | Fraunces, Manrope, DM Mono, Shadows Into Light | `blog3`, `blog4`, `blog8`, `blog-topics`, `mood` |
| **Bodoni editorial** | Bodoni Moda, DM Mono (+ Manrope / Shadows Into Light) | `index`, `about`, `gallery`, `games`, and the six "stamp" pages |
| **Legacy one-offs**: own fonts, external `transparenttextures.com` backgrounds | varies | `blog1`, `blogsecond`, `heyeheyhey`, `loveletter`, `vibes` |

Common patterns inside the newer pages:
- Colours are tokens on `:root` (`--cream`, `--card`, `--ink`, `--wine`, `--rust`, `--red`, tape colours, `--shadow` as bare RGB for `rgba(var(--shadow),a)`). Recolour through the tokens, not by hunting literals.
- Entrance animations are pure CSS transitions armed by an `IntersectionObserver` that adds a class once and then unobserves. Blog pages use `.set`, the gallery uses `.show`, and blog8's extra layer uses `.in`.
- Every page has `prefers-reduced-motion` and `pointer:coarse` blocks that switch off the heavy effects. Keep them when adding motion.
- The like button (`blog4`, `blog8`) is localStorage-only: `LIKE_ENDPOINT = ""` and a per-post `KEY`. Give a new post its own `KEY`.

### Blog posts and the blog index

- `index.html` links to `blog-topics.html`, which is a rack of cards (`a.topic`), newest first. Each card links to one post.
- **To add a post:** copy `blog8.html` (or `blog4.html`) and change the `<title>`, meta description, `.title`, `.caption`, the seal's `<textPath>` text, `.dateline`, the article body, and the like `KEY`. Then, in `blog-topics.html`:
  - add a card at the top of `.rack`
  - move the **single** `<span class="latest">` badge onto it
  - update the "N so far" caption and the `<!-- ─── one ─── -->` numbering comments
  - restagger each card's `--wait` delay
- Card glyphs are small inline SVGs. `--len` is each path's stroke-draw length. `.fill` and `.solid` are fill variants. `.blip`, `.steam`, `.grow`, `.yap` and `.strum` are hover animations already defined in `blog-topics.html`.
- Post filenames are not sequential (`blog1`, `blogsecond`, `blog3`, `blog4`, `blog8`). Pick the next unused number. `blog5`–`blog7` only exist on the backup branch.

### Stamp pages

`comrade`, `hiraeth`, `moonbloom`, `cosmic`, `soulthread` and `vintage` are reached from the stamp grid in `index.html` (thumbnails `images/stamp-*.jpeg`). They link to each other in a chain.

### Gallery

`gallery.html` is a grid of `<div class="slot"><img src="images/gallery-NN.jpeg">` lines. The JS derives the corner numbers, the lightbox, keyboard and swipe navigation, and the `NN / total` counter from the DOM. **To add photos**, put them in `images/` as the next `gallery-NN.jpeg`, add one slot line each, and update the "forty photographs" line under the title.

## Repo layout

- **Pages live at the top level** and must stay there: their filenames are the public URLs (`lavannya.me/blog8.html`), so moving one into a folder breaks shared links and the sitemap. If pages ever do move, add Netlify redirects (`_redirects`) at the same time.
- **Every image lives in `images/`**: `gallery-NN` (gallery), `home-NN` (index), `photoN` (about), `yap-NN` (blog3), `stamp-*` (index stamp grid). The only image at the top level is `favicon.jpeg`, which every page references.
- When the user uploads photos through the GitHub web UI they land at the top level with names like `WhatsApp Image ….jpeg`. Rename them to the next `gallery-NN.jpeg` (or whatever they're for), `git mv` them into `images/`, and check they aren't byte-identical duplicates of an existing image first.

## Known loose ends

- `games.html`, `mood.html`, `heyeheyhey.html` and `vibes.html` have no inbound links.
- `sitemap.xml` lists only `/`, `about`, `gallery` and `vibes`. It doesn't list the blog pages.

## Writing for the blog

When drafting or editing post text:
- Titles are lowercase.
- Spelling is British.
- Apostrophes and quotes are written as entities (`&rsquo;`).
- The user prefers plain, direct, informal wording with easy words.
- Keep the user's own text verbatim unless they ask for edits. When asked to improve it, change only specific paragraphs and report each change.
- The handwriting font (`--hand`) is the author's own voice: captions, margin notes, closing stamps. A quoted line goes in the display serif italic with a `<cite>`, never in the handwriting font, and always credited.
