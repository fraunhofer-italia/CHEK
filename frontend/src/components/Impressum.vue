<template>
  <div class="impressum">
    <nav>
      <RouterLink class="minor-label link" to="/">Back to Main Page</RouterLink>
    </nav>
    <div class="container">
      <h1>Impressum</h1>

      <h2>Company Information</h2>
      <p><strong>Name:</strong> Fraunhofer Italia Research</p>
      <p><strong>Address:</strong><br>
        Via A. Volta 13/A<br>
        39100 Bolzano (BZ)<br>
        Italia</p>
      <p><strong>Email Address:</strong> <a href="mailto:info@fraunhofer.it">info@fraunhofer.it</a></p>
      <p><strong>VAT ID:</strong> IT02654700216</p>

      <h2>Usage Rights</h2>
      <p>© Fraunhofer Italia s.c.a.r.l., Bolzano. All rights reserved.</p>
      <p>All copyright for this website is owned in full by Fraunhofer Italia.</p>
      <ul>
        <li>Material may be downloaded or printed for <strong>personal use only</strong>.</li>
        <li>Any commercial use or distribution is <strong>strictly forbidden</strong> without prior written approval.
        </li>
      </ul>

      <h3>Exceptions for Press Use:</h3>
      <ul>
        <li>Material may be used in <strong>press reports</strong> on Fraunhofer-Gesellschaft and its institutes.</li>
        <li><strong>Conditions:</strong>
          <ul>
            <li>No alterations to pictorial content (except framing modifications).</li>
            <li>Source attribution is required.</li>
            <li>Two free reference copies must be sent to the above address.</li>
            <li>Usage is free of charge.</li>
          </ul>
        </li>
      </ul>

      <h2>Disclaimer</h2>
      <ul>
        <li>We <strong>do not assume liability</strong> for the content of external linked pages. The respective
          operators are responsible for their content.</li>
        <li>We strive to keep this website <strong>accurate, complete, and up to date</strong>, but errors may still
          occur.</li>
        <li>We <strong>disclaim liability</strong> for any material or non-material loss incurred due to reliance on
          website content.</li>
      </ul>

      <h3>Trademark & Copyright Notice:</h3>
      <p>Registered trademarks, proprietary names, and copyrighted text/images may not always be explicitly marked.</p>
      <p>The absence of such indications <strong>does not imply</strong> that these names, images, or texts belong to
        the public domain under trademark or copyright law.</p>
    </div>
  </div>
</template>

<script setup>
</script>

<style scoped>
.impressum {
  font-family: Montserrat;
  line-height: 1.6;
  max-width: 800px;
  width: 100%;
  padding: 20px;
  background: white;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
  border-radius: 8px;
  justify-content: flex-start;
  align-items: flex-start;
}

.impressum h1 {
  font-size: 2em;
  margin-bottom: 0.5em;
}

.impressum h2 {
  font-size: 1.5em;
  margin-top: 1em;
  margin-bottom: 0.5em;
}

.impressum p,
.impressum ul {
  margin-bottom: 1em;
}

.impressum ul {
  list-style-type: disc;
  padding-left: 20px;
}
</style>