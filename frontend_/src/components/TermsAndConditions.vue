<template>
  <div class="terms-and-conditions">
    <nav>
      <RouterLink class="minor-label link" to="/register">Back to registration</RouterLink>
    </nav>
    <nav>
      <RouterLink class="minor-label link" to="/">Back to main page</RouterLink>
    </nav>
    <div class="container">
      <h1>Terms and Conditions</h1>

      <h2>Introduction</h2>
      <p>Welcome to our website. By accessing and using this website, you agree to be bound by these Terms and
        Conditions, as well as our Privacy Policy. If you do not agree with any part of these terms, please do not use
        our services.</p>

      <h2>Use of the Website</h2>
      <ul>
        <li>This website is designed to assist users in creating a process map and guiding them through the change
          management process related to the digitalization of the building permit.</li>
        <li>The content is for general informational purposes only and may be updated without prior notice.</li>
        <li>We reserve the right to modify, suspend, or discontinue any aspect of our services without liability.</li>
      </ul>

      <h2>User Responsibilities</h2>
      <ul>
        <li>You agree to use this website only for lawful purposes.</li>
        <li>Unauthorized use, including but not limited to hacking, distributing malware, or attempting to disrupt
          service functionality, is strictly prohibited.</li>
        <li>Any misuse of our service may result in termination of access.</li>
      </ul>

      <h2>Intellectual Property</h2>
      <p>The design, content, layout, and graphics on this website are owned by or licensed to us. Reproduction or
        redistribution of any content is prohibited unless explicitly permitted in writing.</p>

      <h2>Limitation of Liability</h2>
      <p>We do not guarantee the accuracy, completeness, or suitability of the information and tools provided. The
        website and services are provided "as is" without warranties of any kind, express or implied.</p>
      <p>We are not liable for any direct, indirect, incidental, or consequential damages resulting from the use of this
        website.</p>

      <h2>Third-Party Links</h2>
      <p>Our website may contain links to external websites. We are not responsible for the content or privacy practices
        of such sites. Users should review the terms and policies of any third-party websites they visit.</p>

      <h2>Governing Law</h2>
      <p>These Terms and Conditions are governed by the laws of the European Union and the country in which our company
        is based. Any disputes will be subject to the jurisdiction of the appropriate courts within this legal
        framework.</p>

      <h2>Changes to Terms</h2>
      <p>We reserve the right to update these Terms and Conditions at any time. Continued use of the website after
        updates constitutes acceptance of the revised terms.</p>

    </div>
  </div>
</template>

<script setup>
</script>

<style scoped>
.terms-and-conditions {
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

.terms-and-conditions h1 {
  font-size: 2em;
  margin-bottom: 0.5em;
  text-align: center;
}

.terms-and-conditions h2 {
  font-size: 1.5em;
  margin-top: 1em;
  margin-bottom: 0.5em;
}

.terms-and-conditions p,
.terms-and-conditions ul {
  margin-bottom: 1em;
}

.terms-and-conditions ul {
  list-style-type: disc;
  padding-left: 20px;
}
</style>