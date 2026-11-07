# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is, and who you're talking to

Lavannya Daigavane's personal site, live at **https://lavannya.me**: her writing, poems and photographs. It's hand-written static HTML with no build step, framework, package manager or test suite.

**You'll usually be talking to Lavannya herself.** Her brother set up the repo, deployment and tooling in November 2026 and handed it over. Assume she knows what she wants the site to look and read like, but not git, HTML or SEO. So:
- Explain in plain words what you changed and what visitors will see. Skip jargon, or explain it in one clause.
- Run the commands yourself. Don't hand her terminal steps unless something needs her own login (see "Deploying").
- Before anything goes live, tell her in a sentence what will change on the site and ask.

## The workflow for every change

1. Make the edit.
2. Run `python tools/site.py`. It must end with **`all good.`** If it prints PROBLEMS, fix them first.
3. Commit.
4. Ask Lavannya whether to put it live. On a yes, `git push`.
5. Check the live site with `curl` a minute later: the page returns 200, and new images load.

## Commands

```bash
python tools/site.py          # SEO tags, sitemap, gallery thumbnails, and a full site check
python -m http.server 8000    # preview locally at http://localhost:8000/blog8.html etc.
curl -sI https://lavannya.me/blog8.html   # check the live site (see the CA note below)
```

`tools/site.py` needs Pillow for thumbnails (`pip install pillow`, already installed on this machine).

## Deploying

Pushing `main` to GitHub (`github.com/lavannyadaigavane/website`) triggers **Netlify**, which publishes to lavannya.me in about a minute. GitHub Pages is not used, so ignore `has_pages: false`.

- **Ask before every `git push`**, because a push publishes straight to the live site. Never force-push.
- If a push fails with "Invalid username or token", the saved GitHub login has expired. Only Lavannya can fix this. She removes `git:https://github.com` from Windows **Credential Manager**, then runs `git push` once in the VS Code terminal and signs in through the browser window that opens.
- If she's been uploading files through the GitHub website, `git pull` before starting work.
- Branch `local-backup-2026-11-07` holds this folder's state from before it was synced with GitHub, including the unlinked drafts `blog5`–`blog7.html`. Leave it alone unless asked.
- Python 3.10 on this machine has an outdated CA bundle, so `urllib` fails TLS against lavannya.me. Use `curl`.

## SEO: handled by `tools/site.py`, don't do it by hand

The script owns, and rewrites on every run:
- the block between `<!-- seo:start -->` and `<!-- seo:end -->` in each page's `<head>`: canonical URL, Open Graph and Twitter tags (link previews on WhatsApp, Instagram and iMessage), and JSON-LD (`Person` on the homepage, `BlogPosting` on posts). Never edit inside that block.
- `sitemap.xml`.

It reads from two places:
- **Each page's own `<title>` and `<meta name="description">`.** Every public page needs both, and each description must be unique, short and specific to that page. The script fails on a missing description, and on one copied from another page. That's the usual mistake when a new post starts as a copy of an old one.
- **The `PAGES` list at the top of `tools/site.py`.** Every `.html` file must be listed there, or the script fails. Each entry is one of:
  - `"home"`
  - `"page"`
  - `("post", "YYYY-MM-DD")`
  - `"hidden"`: `noindex` and left out of the sitemap

  `games`, `mood`, `heyeheyhey` and `vibes` are hidden because nothing links to them. When one gets a link, change it to `"page"` and rerun.

The link-preview image for every page is `images/og/lavannya.jpg` (1200×630, cropped from `images/home-07.jpeg`). If a page should preview with its own image, extend `seo_block()` in the script rather than hand-writing tags.

Google Search Console isn't confirmed to be set up. If Lavannya asks why the site doesn't show up on Google, start there: she verifies `lavannya.me` and submits `https://lavannya.me/sitemap.xml`. That step needs her Google login.

## Architecture

**Every page is self-contained.** Each `.html` file carries its own `<style>`, `<script>` and Google Fonts link. Nothing is shared at build time. Changing the look of one page never affects another, and a fix to a shared pattern (nav, like button) has to be repeated in each file.

Pages fall into three design families. Match the family you're editing:

| Family | Fonts | Pages |
|---|---|---|
| **Paper scrapbook**: cream graph-paper ground, taped sheets, wax seal, handwriting | Fraunces, Manrope, DM Mono, Shadows Into Light | `blog3`, `blog4`, `blog8`, `blog-topics`, `mood` |
| **Bodoni editorial** | Bodoni Moda, DM Mono (+ Manrope / Shadows Into Light) | `index`, `about`, `gallery`, `games`, and the six poem pages |
| **Legacy one-offs**: own fonts, external `transparenttextures.com` backgrounds | varies | `blog1`, `blogsecond`, `heyeheyhey`, `loveletter`, `vibes` |

Common patterns inside the newer pages:
- Colours are tokens on `:root` (`--cream`, `--card`, `--ink`, `--wine`, `--rust`, `--red`, tape colours, `--shadow` as bare RGB for `rgba(var(--shadow),a)`). Recolour through the tokens, not by hunting literals.
- Entrance animations are pure CSS transitions armed by an `IntersectionObserver` that adds a class once and then unobserves. Blog pages use `.set`, the gallery uses `.show`, and blog8's extra layer uses `.in`.
- Every page has `prefers-reduced-motion` and `pointer:coarse` blocks that switch off the heavy effects. Keep them when adding motion.
- The like button (`blog4`, `blog8`) is localStorage-only: `LIKE_ENDPOINT = ""` and a per-post `KEY`. Give a new post its own `KEY`.

### Adding a blog post

1. Copy `blog8.html` (or `blog4.html`) to the next unused filename. The numbers aren't sequential: `blog1`, `blogsecond`, `blog3`, `blog4` and `blog8` exist, and `blog5`–`7` only exist on the backup branch.
2. Change the `<title>`, the **meta description**, `.title`, `.caption`, the seal's `<textPath>` text, `.dateline`, the article body, and the like `KEY`.
3. In `blog-topics.html` (the rack of `a.topic` cards, newest first):
   - add a card at the top of `.rack`
   - move the **single** `<span class="latest">` badge onto it
   - update the "N so far" caption and the `<!-- ─── one ─── -->` numbering comments
   - restagger each card's `--wait` delay

   Card glyphs are small inline SVGs: `--len` is each path's stroke-draw length, `.fill` and `.solid` are fill variants, and `.blip`, `.steam`, `.grow`, `.yap` and `.strum` are hover animations already defined in that file.
4. Add `"blogN.html": ("post", "YYYY-MM-DD")` to `PAGES` in `tools/site.py`, then run it.

### Poem pages

`comrade`, `hiraeth`, `moonbloom`, `cosmic`, `soulthread` and `vintage` are one poem each, reached from the stamp grid in `index.html` (thumbnails `images/stamp-*.jpeg`). They link to each other in a chain.

### Gallery

`gallery.html` is a grid of slot lines:

```html
<div class="slot"><img src="images/thumbs/gallery-NN.jpeg" data-full="images/gallery-NN.jpeg" alt="" loading="lazy"></div>
```

The grid loads the ~300px thumbnail, and the lightbox loads `data-full` only when a photo is opened. The JS derives the corner numbers, the lightbox, keyboard and swipe navigation, and the `NN / total` counter from the DOM.

**To add photos:**
1. Put each one in `images/` as the next `gallery-NN.jpeg`.
2. Add a slot line for each.
3. Update the "forty photographs" line under the title.
4. Run `tools/site.py`, which makes the missing thumbnails.

## Repo layout

- **Pages live at the top level** and must stay there. Their filenames are the public URLs (`lavannya.me/blog8.html`), so moving one into a folder breaks shared links and Google's index. If pages ever do move, add Netlify redirects (`_redirects`) in the same change.
- **Every image lives in `images/`:**
  - `gallery-NN`, plus `thumbs/` (generated)
  - `home-NN` (index)
  - `photoN` (about)
  - `yap-NN` (blog3)
  - `stamp-*` (index)
  - `og/` (link preview)

  The only image at the top level is `favicon.jpeg`.
- Photos uploaded through the GitHub website land at the top level with names like `WhatsApp Image ….jpeg`. Check they aren't byte-identical to an existing image, rename them to what they're for, and `git mv` them into `images/`.
- `tools/` is published by Netlify along with everything else. That's harmless, but don't put anything private there.

## Known loose ends

- Full-size photos are heavy. `images/` holds about 15 MB, some photos are over 1 MB each, and the homepage and about page load their photos at full size. Compressing them is a worthwhile future job. Keep originals in git history.
- `blog3.html` has a second, empty `<h1 id="rtitle">` that its pop-up reader fills in. It's harmless; changing it risks that page's CSS.
- The caption under `blog8`'s title is a line from Sylvia Plath's *The Bell Jar* with no credit. It was flagged and left as is at the time. Raise it again if that page is being edited.

## Writing for the blog

When drafting or editing post text:
- Titles are lowercase.
- Spelling is British.
- Apostrophes and quotes are written as entities (`&rsquo;`).
- Lavannya prefers plain, direct, informal wording with easy words.
- Keep her own text verbatim unless she asks for edits. When asked to improve it, change only specific paragraphs and report each change.
- The handwriting font (`--hand`) is her own voice: captions, margin notes, closing stamps. A quoted line goes in the display serif italic with a `<cite>`, never in the handwriting font, and is always credited.
