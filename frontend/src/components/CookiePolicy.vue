<template>
  <div class="cookie-policy">
    <nav>
      <RouterLink class="minor-label link" to="/">Back to Main Page</RouterLink>
    </nav>
    <div class="container">
      <h1>Privacy and Cookie Policy</h1>

      <h2>1. Introduction</h2>
      <p>This page explains how we collect, use, and protect your personal data, as well as how we use cookies and
        similar technologies.</p>

      <h2>2. Privacy Policy</h2>

      <h3>2.1 Data Controller</h3>
      <p><strong>Fraunhofer Italia Research s.c.a.r.l.</strong><br>
        Via A. Volta 13/A, 39100 Bolzano, Italy<br>
        Email: <a href="mailto:info@fraunhofer.it">info@fraunhofer.it</a></p>

      <h3>2.2 Personal Data We Collect</h3>
      <ul>
        <li><strong>Registration information:</strong> Name, email address, and any details you provide during sign-up.
        </li>
        <li><strong>Session data:</strong> Authentication tokens stored in <code>sessionStorage</code>.</li>
        <li><strong>Project data:</strong> Information related to your activities on the platform.</li>
        <li><strong>Analytics data:</strong> Google Analytics (with IP anonymization).</li>
      </ul>

      <h3>2.3 User Rights</h3>
      <p>Under GDPR, you have the right to access, rectify, delete, and transfer your personal data, and to withdraw
        consent at any time. To exercise these rights, contact us at <a
          href="mailto:info@fraunhofer.it">info@fraunhofer.it</a>.</p>

      <h2>3. Cookie Policy</h2>

      <h3>3.1 What Are Cookies?</h3>
      <p>Cookies are small files stored on your device that improve your browsing experience and provide core
        functionalities such as session management and security.</p>

      <h3>3.2 Cookies We Use</h3>
      <ul>
        <li><strong>Essential Cookies:</strong> Necessary for authentication and session management.</li>
        <li><strong>Analytics Cookies:</strong> Used to track website traffic (<strong>Google Analytics</strong> with IP
          anonymization).</li>
        <li><strong>Security Cookies:</strong> Used to protect our platform (<strong>Google reCAPTCHA</strong>).</li>
      </ul>

      <h3>3.3 Session Storage</h3>
      <p>We use <code>sessionStorage</code> to temporarily store authentication tokens and project-related data. This
        data is automatically deleted when you close your browser.</p>

      <h2>4. Third-Party Services</h2>
      <p>We use third-party services to enhance our platform:</p>
      <ul>
        <li><strong>Google Analytics:</strong> Used to analyze website traffic while ensuring IP anonymization. <a
            href="https://policies.google.com/privacy" target="_blank">Google Privacy Policy</a></li>
        <li><strong>Google reCAPTCHA:</strong> Used for spam protection. <a href="https://policies.google.com/privacy"
            target="_blank">Google Privacy Policy</a></li>
      </ul>

      <h2>5. Contact Information</h2>
      <p>If you have any questions about this Privacy and Cookie Policy, please contact us at:</p>
      <p><strong>Fraunhofer Italia Research s.c.a.r.l.</strong><br>
        Via A. Volta 13/A, 39100 Bolzano, Italy<br>
        Email: <a href="mailto:info@fraunhofer.it">info@fraunhofer.it</a></p>
    </div>
  </div>
</template>

<script setup>
</script>

<style scoped>
.cookie-policy {
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

.cookie-policy h1 {
  font-size: 2em;
  margin-bottom: 0.5em;
}

.cookie-policy h2 {
  font-size: 1.5em;
  margin-top: 1em;
  margin-bottom: 0.5em;
}

.cookie-policy p,
.cookie-policy ul {
  margin-bottom: 1em;
}

.cookie-policy ul {
  list-style-type: disc;
  padding-left: 20px;
}
</style>
