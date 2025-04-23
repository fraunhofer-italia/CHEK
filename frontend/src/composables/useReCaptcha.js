// src/composables/useReCaptcha.js
import { ref } from 'vue';

export default function useReCaptcha() {
  const token = ref('');

  const loadRecaptcha = () => {
    return new Promise(resolve => {
      if (typeof grecaptcha !== 'undefined') {
        resolve(grecaptcha);
      } else {
        window.addEventListener('load', () => {
          resolve(grecaptcha);
        });
      }
    });
  };

  const executeRecaptcha = async (action) => {
    const recaptcha = await loadRecaptcha();
    token.value = await recaptcha.execute('6LdFeQ0qAAAAAIwtRPuINcO7B-g_IBr2IxZ3D04t', { action });
  };

  return {
    token,
    executeRecaptcha
  };
}
