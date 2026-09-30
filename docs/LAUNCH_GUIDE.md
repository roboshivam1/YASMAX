# Launch Guide (for Shivam)

How to publish YASMAX on GitHub Pages, ship the offline download, update it and look
after it. Commands run from the repo root in your terminal. About 30 minutes the
first time.

---

## 0. Before you launch

- [ ] `(cd engine && pytest -q)` passes and `python3 tools/build_site.py` finishes.
- [ ] Try the built site locally, exactly as it will be published:
      `python3 tools/build_site.py && python3 tools/serve.py --dir _site --open`.
      Click around, then in Chrome's DevTools > Application > Service workers,
      tick *Offline* and reload: it must still work.
- [ ] Check it once in **Safari** (the Mac default) and in **Firefox**. Only Chromium
      has been tested so far.
- [ ] Lab check of the most important guesses (`docs/RESEARCH.md` > Lab checklist).
      At minimum: what `OUT #65, 0` and `OUT #65, 1` print, and the HLT message text.
- [ ] Email the original author (draft in section 6). Not legally required to try
      things out, but it is the right thing before sharing widely, and he can
      answer our open questions.
- [ ] Licence: `LICENSE` is PolyForm Noncommercial 1.0.0 with your name. Keep it or
      change it now, because changing it later is messy.

---

## 1. Put the code on GitHub (one time)

Your repo already exists: `github.com/roboshivam1/YASMAX`. If this folder is not
connected to it yet:

```bash
git init
git add -A
git commit -m "YASMAX 0.6.0: first public version"
git branch -M main
git remote add origin https://github.com/roboshivam1/YASMAX.git
git push -u origin main
```

If it is already connected, just commit and push:

```bash
git add -A
git commit -m "Launch: offline app, docs, credits"
git push
```

Check the default branch name on GitHub (repo main page, branch dropdown). The deploy
workflow runs on `main` or `master`. The links in `.github/ISSUE_TEMPLATE/config.yml`
use `main`.

The generated folders (`_site/`, `dist/`, `web/engine.zip`) are in `.gitignore`. Do not
commit them; GitHub builds them.

---

## 2. Turn on GitHub Pages (one time)

1. On GitHub: **Settings > Pages**.
2. Under **Build and deployment > Source**, choose **GitHub Actions**. Not "Deploy
   from a branch".
3. That's all. Pushing to `main` now runs `.github/workflows/deploy.yml`, which:
   - tests the engine (a failing test stops the deploy, so a broken engine never goes live),
   - runs `tools/build_site.py`: engine, Pyodide copy, icons, build stamp, precache list,
   - publishes `_site/`.
4. Watch it under the **Actions** tab. The first run takes about 2 minutes. When it
   is green, the site is at **<https://roboshivam1.github.io/YASMAX/>**. The URL is
   also shown in Settings > Pages and on the deploy job.

If the first deploy fails with a Pages or environment error, check step 2 again:
Source must be "GitHub Actions". Then re-run the job (Actions > the failed run >
**Re-run jobs**). You can also start a deploy by hand: Actions > *Deploy to GitHub
Pages* > **Run workflow**.

### Check the live site
- It loads, and the footer shows your credit.
- The **CPU Help** tab's last line shows a build like `0.6.0-a1b2c3d` (not `dev`).
- Chrome offers **Install** in the address bar.
- DevTools > Application > Service workers shows `sw.js` activated. Tick
  *Offline*, reload, and it still works.

---

## 3. Optional: your own address (yasmax.shvmkpr.in)

1. At your domain registrar's DNS settings for `shvmkpr.in`, add a record:
   **CNAME**, name `yasmax`, value `roboshivam1.github.io`.
2. GitHub **Settings > Pages > Custom domain**: enter `yasmax.shvmkpr.in`, click
   **Save**, and wait for the DNS check to pass (minutes to a few hours).
3. Tick **Enforce HTTPS** once it becomes available. Offline mode and app install
   need HTTPS.
4. Update the links in `README.md` and `docs/USER_GUIDE.md` to the new address.

With Actions-based publishing you do not need a `CNAME` file in the repo.

---

## 4. Releasing the offline download

The offline zip is built and attached to a GitHub Release when you push a version
tag:

```bash
git tag v0.6.0
git push origin v0.6.0
```

`.github/workflows/release.yml` tests, builds `dist/yasmax-offline-0.6.0.zip` and
creates the release with it. The release appears under **Releases** on the repo
page, where the user guide points students.

To try the zip before tagging: `python3 tools/build_site.py --zip`, then unzip
`dist/yasmax-offline-*.zip` somewhere and run its start script.

---

## 5. Updating after launch

1. Make the change, bump the version in **two** places:
   `engine/yasmax_engine/__init__.py` and `engine/pyproject.toml`.
2. Add a line to `CHANGELOG.md`.
3. `git commit` and `git push`. The site redeploys by itself.
4. Students' open copies notice the new version and show **"A new version is
   ready: reload"** in the footer. The service worker keeps one cache per build, so
   nobody gets stuck on an old copy.
5. For a new offline zip, push a new tag (`v0.6.1` ...).

**Updating Pyodide:** change `PYODIDE_VERSION` in **both** `web/js/worker.js` and
`tools/build_site.py`, run the tests and try the site locally before pushing.

**Rolling back a bad deploy:** `git revert <bad commit>` and `git push`. Or, on the
Actions tab, open the last good *Deploy* run and click **Re-run jobs**.

---

## 6. Email to the original author (draft)

Find his current address on [teach-sim.com](https://teach-sim.com/) (Contact).

> Subject: A browser recreation of the CPU Simulator for Mac/Linux students
>
> Dear Dr Mustafa,
>
> I'm Shivam Kapoor, a first-year Computer Science student at LNMIIT Jaipur. We use
> the CPU-OS Simulator (7.5.50) in our Computer Organization & Architecture labs.
> Many classmates use Macs and can't run it at home, so as a learning project I built
> YASMAX, a free, non-commercial browser recreation of the CPU Simulator window:
> https://roboshivam1.github.io/YASMAX/ (source: https://github.com/roboshivam1/YASMAX).
>
> It credits you and the simulator prominently and says it is not affiliated with or
> endorsed by you. I wanted to ask for your blessing before sharing it more widely,
> and to ask whether you would prefer any changes to the name, the look or the credit.
>
> If you have a moment, I would also be grateful for help with a few behaviours I
> could only guess (for example the second operand of OUT and the SR bit layout),
> so students don't learn anything wrong.
>
> Thank you for creating such a useful teaching tool.
>
> Best regards,
> Shivam Kapoor
> https://shvmkpr.in

If he asks you to change or take something down, do it promptly.

---

## 7. Telling people

A message for your class group:

> Made something for the Mac/Linux people 👋 **YASMAX**, a browser version of the
> YASMIN CPU Simulator we use in CO&A labs. It has the same window and instructions,
> and it opens and saves the lab's .sas files.
> Open: https://roboshivam1.github.io/YASMAX/ (Chrome: click Install to get it as an app; works offline)
> It's for practice: if anything behaves differently from the lab version, please
> report it (link in the CPU Help tab) with a screenshot of both. That's how it gets exact.

---

## 8. After launch

- **Issues tab:** difference reports are the priority. For each one, confirm it in the
  lab, fix it, move the item from "Provisional" to "Answered" in `docs/RESEARCH.md`,
  and remove the row from the README's guesses table.
- **Turn each confirmed difference into a test** in `engine/tests/unit/test_cpu.py`,
  so it can never come back.
- **YASMIN 8.5** is announced on teach-sim.com. When the lab switches, compare the
  new instruction window and main window against YASMAX.
- Things still to build: the new 7.5.50 op codes (CVS, CVI, LNS ...), UNDO,
  SHOW..., the Watch / Program Stack / CPU View tabs, and Exec. Clocks.
