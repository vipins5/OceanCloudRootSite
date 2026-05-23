(function () {
  'use strict';

  function getCanonicalUrl() {
    var canonical = document.querySelector('link[rel="canonical"]');
    return canonical ? canonical.href : window.location.href.split('#')[0];
  }

  function getTitle() {
    var ogTitle = document.querySelector('meta[property="og:title"]');
    if (ogTitle && ogTitle.content) return ogTitle.content;
    var h1 = document.querySelector('.article-hero h1, h1');
    return h1 ? h1.textContent.trim().replace(/\s+/g, ' ') : document.title.replace(/\s*\|\s*OceanCloud\s*$/, '');
  }

  function copyToClipboard(text, button) {
    var reset = function () {
      setTimeout(function () {
        button.classList.remove('copied');
        button.querySelector('.share-copy-text').textContent = 'Copy link';
      }, 1800);
    };

    var done = function () {
      button.classList.add('copied');
      button.querySelector('.share-copy-text').textContent = 'Copied';
      reset();
    };

    if (navigator.clipboard && window.isSecureContext) {
      navigator.clipboard.writeText(text).then(done).catch(function () { fallbackCopy(text, done); });
    } else {
      fallbackCopy(text, done);
    }
  }

  function fallbackCopy(text, done) {
    var area = document.createElement('textarea');
    area.value = text;
    area.setAttribute('readonly', '');
    area.style.position = 'fixed';
    area.style.opacity = '0';
    document.body.appendChild(area);
    area.select();
    try { document.execCommand('copy'); } catch (error) {}
    area.remove();
    done();
  }

  function initArticleShare() {
    var article = document.querySelector('.article-wrap');
    var meta = document.querySelector('.article-meta');
    if (!article || !meta || document.querySelector('.article-share')) return;

    var url = getCanonicalUrl();
    var title = getTitle();
    var encodedUrl = encodeURIComponent(url);
    var encodedTitle = encodeURIComponent(title);

    var share = document.createElement('div');
    share.className = 'article-share';
    share.setAttribute('aria-label', 'Share this article');
    share.innerHTML =
      '<span class="article-share-label">Share</span>' +
      '<a class="article-share-btn" href="https://www.linkedin.com/sharing/share-offsite/?url=' + encodedUrl + '" target="_blank" rel="noopener noreferrer" aria-label="Share on LinkedIn"><span aria-hidden="true">in</span></a>' +
      '<a class="article-share-btn" href="https://twitter.com/intent/tweet?url=' + encodedUrl + '&text=' + encodedTitle + '" target="_blank" rel="noopener noreferrer" aria-label="Share on X"><span aria-hidden="true">X</span></a>' +
      '<button class="article-share-btn article-share-copy" type="button" aria-label="Copy article link"><span class="share-copy-text">Copy link</span></button>';

    meta.insertAdjacentElement('afterend', share);

    var copyButton = share.querySelector('.article-share-copy');
    if (copyButton) {
      copyButton.addEventListener('click', function () {
        copyToClipboard(url, copyButton);
      });
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initArticleShare);
  } else {
    initArticleShare();
  }
})();
