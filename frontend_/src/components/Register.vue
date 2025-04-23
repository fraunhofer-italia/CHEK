<template>
    <div id="register-container">
        <div id="register-header">
            <div class="main-heading-small">
                Define your Building Permit process, assess your Maturity and create a personalized Roadmap towards a Digital Building Permit.
            </div>
        </div>
        <form id="register-info" @submit.prevent="register">
            <div class="input-h-container">
                <input class="register-user-input" type="text" id="fname" name="first_name" placeholder="First Name">
                <input class="register-user-input" type="text" id="lname" name="last_name" placeholder="Last Name">
            </div>
            <input class="register-user-input" type="text" id="country" name="country" placeholder="Country">
            <div class="input-h-container"  id="location-input">
                <input class="register-user-input" type="text" id="zipcode" name="zip_code" placeholder="Postal Code">
                <input class="register-user-input" type="text" id="muni" name="municipality" placeholder="Municipality">
            </div>
            <input class="register-user-input" type="text" id="city" name="city" placeholder="City">
            <!-- <input class="register-user-input" type="text" id="lang" name="language" placeholder="Language"> -->
            <input class="register-user-input" type="text" id="email" name="email" placeholder="E-Mail">
            <div class="input-h-container"  id="location-input">
                <input class="register-user-input" type="password" id="password1" name="password1" placeholder="Password">
                <input class="register-user-input" type="password" id="password2" name="password2" placeholder="Repeat password">
            </div>

            <RouterLink class="minor-label link small" to="/terms-and-conditions">By registering you accept our terms and conditions</RouterLink>

            <button type="submit" id="reg-btn" class="register-btn">
                Register
            </button>
            <RouterLink class="minor-label link" to="/login">Back to Login</RouterLink>
        </form>
        <div id="logos-footer">
            <img class="logo" src="./images/eu_full_logo.png" alt="eu-logo"/>
            <img class="logo" src="./images/check_full_logo.png" alt="check-logo"/>
            <img class="logo" src="./images/fhi_full_logo.png" alt="fhi-logo"/>
        </div>

        <div class="logos-footer">
            <RouterLink :to="{name: 'impressum'}" class="footer-btn-label">
                Impressum
            </RouterLink>
            <RouterLink :to="{name: 'termsAndConditions'}" class="footer-btn-label">
                Terms and Conditions
            </RouterLink>
            <RouterLink :to="{name: 'cookiePolicy'}" class="footer-btn-label">
                Privacy & Cookie Policy
            </RouterLink>
        </div>

    </div>
    <div id="back-pic">

    </div>
</template>

<script setup>
import { inject, onMounted} from "vue";

import useReCaptcha from '../composables/useReCaptcha';
const { token, executeRecaptcha } = useReCaptcha();
const action = 'chek_register_user'; // Define your action name here


const base_api = inject('base_api');
const register_api = base_api +"/users/";

onMounted(()=>{
    console.log(`register_api: ${register_api}`);
});

async function register(){
    const fname = document.getElementById('fname');
    const lname = document.getElementById('lname');
    const country = document.getElementById('country');
    const zipcode = document.getElementById('zipcode');
    const city = document.getElementById('city');
    const muni = document.getElementById('muni');
    // const lang = document.getElementById('lang');
    const email = document.getElementById('email');
    const password1 = document.getElementById('password1');
    const password2 = document.getElementById('password2');

    const input_list = [fname, lname, country, zipcode, city, muni, email];
    const user_data = {};
    // Allow only English for the moment
    user_data["language"] = "English";

    let check_complete = true;
    for(let inp of input_list){
        if(inp.value.trim() == ""){
            check_complete = false;
            inp.classList.toggle('alert-input');
            inp.value = "";
            setTimeout(() => {
                inp.classList.toggle('alert-input');
                }, 2500);
        }else{
            user_data[inp.name] = inp.value;
        }
    }

    if(password1.value != password2.value || password1.value =="" || password2.value == ""){
        check_complete = false;
        password1.classList.toggle('alert-input');
        password2.classList.toggle('alert-input');
        setTimeout(() => {
            password1.classList.toggle('alert-input');
            password2.classList.toggle('alert-input');
            }, 2500);
    }else{
        user_data["password"] = password1.value;
    }

    if (!check_complete){
        return;
    }

    await executeRecaptcha(action); // Ensure reCAPTCHA token is retrieved before submission
    user_data["recaptcha_token"] = token.value;
    
    const register_btn = document.getElementById('reg-btn');
    const saved_text = register_btn.textContent;
    register_btn.disabled = true;

    const loading_spinner = document.createElement("div");
    loading_spinner.className = "load-btn";
    register_btn.appendChild(loading_spinner);


    try{
    const res = await fetch(register_api, {
        method: 'POST',
        credentials: 'same-origin',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(user_data),
    })


        const resData = await res.json();
        console.log(resData);
        if(res.ok){
            register_btn.classList.toggle('success-btn');
            register_btn.textContent = "Registration completed!";
        }else{
            register_btn.classList.toggle('fail-btn');
            register_btn.textContent = resData.detail;
            setTimeout(() => {
                register_btn.classList.toggle('fail-btn');
                register_btn.textContent = saved_text;
                register_btn.disabled = false;
            }, 3000);
        }
    }catch(error){
        console.log(error);
        register_btn.classList.toggle('fail-btn');
        register_btn.textContent = "Registration failed! Contact support.";
        setTimeout(() => {
            register_btn.classList.toggle('fail-btn');
            register_btn.textContent = saved_text;
            register_btn.disabled = false;
        }, 3000);
    }


}
</script>

<style>
    #register-container{
        grid-row-start: 1;
        grid-row-end: -1;
        grid-column-start: 1;
        grid-column-end: -1;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        align-items: center;
        gap: 2rem;
        z-index: 1;
        padding: 3rem;
        justify-self: center;
    }
        #register-header{
            display: flex;
            flex-direction: column;
            gap: 1rem;
            max-width: 85vw;
        }
            .main-heading-small {
                color: var(--noble-black-600, #1A1D21);
                text-align: center;
                font-feature-settings: 'liga' off;
                /* Heading S/Regular */
                font-family: Montserrat;
                font-size: 1.875rem;
                font-style: normal;
                font-weight: 400;
                line-height: 2.375rem; /* 126.667% */
            }

        #register-info{
            display: flex;
            flex-direction: column;
            justify-content: center;
            min-width: 30vw;
            gap: 1rem;
    
        }
            .register-user-input{
                outline: none;
                height: 2rem;
                /* width: 100%; */
                /* flex-grow: 1;
                flex-shrink: 1; */
                flex: auto;
                padding: 0.25rem 0.5rem;
                border-radius: var(--input-l, 0.625rem);
                border: 1px solid var(--neutral-100, #DCDEE2);
                background: var(--neutral-0, #FFF);
                color: var(--neutral-600, #525C6C);
                font-feature-settings: 'case' on, 'liga' off;
                /* Input/L */
                font-family: Arial, Helvetica, sans-serif;
                font-size: 1rem;
                font-style: normal;
                font-weight: 600;
                line-height: normal;
            }
            .alert-input{
                    border: 2px solid var(--error--700);
                }
            .register-btn{
                display: flex;
                width: 100%;
                align-items: center;
                padding: 0.75rem 1rem;
                gap: 1rem;
                border-radius: var(--button-l, 0.75rem);
                background: var(--brand-600, #65BEDA);
                color: #f3f3f3;
                /* outline: none; */
                border: none;
                justify-content: center;
                font-feature-settings: 'case' on, 'liga' off;
                /* Input/L */
                font-family: Arial, Helvetica, sans-serif;
                font-size: 1rem;
                font-style: normal;
                font-weight: 600;
                line-height: normal;
                cursor: pointer;
            }
            .success-btn{
                background: var(--stem-green-700, #a3df88);
                color: #f3f3f3;
            }
            .fail-btn{
                background: var(--red-power-600, #d0302f);
                color: #f3f3f3;
            }

            .alert-input{
                border: 2px solid var(--error--700);
            }

            .input-h-container{
                display: flex;
                flex-direction: row;
                justify-content: space-between;
                gap:1rem;
                width: 100%;
            }

        #logos-footer{
            display: flex;
            flex-direction: row;
            max-height: 4rem;
            gap:2rem;
            justify-content: center;
            align-items: center;
            z-index: 1;
        }
            .logo{
                height: 3rem;
                width: auto;
                object-fit: contain;

            }
            #back-pic{
                position: absolute;
                top: 40vh;
                left: 0;
                margin: 0;
                border: none;
                width: 100%;
                height: 60vh;
                /* object-fit: contain; */
                background: center / cover no-repeat url(images/login_background.png);
                opacity: 0.5;
                z-index: 0;
            }
        .footer-btn-label{
          color: var(--noble-black-400);
          font-feature-settings: 'liga' off;
          /* Paragraph M/Bold */
          font-family: MyriadPro;
          font-size: 1rem;
          font-style: normal;
          font-weight: 200;
          line-height: 1.5rem; /* 150% */
        }
        .small{
            font-size: 0.8rem;
            /* color: var(--neutral-600, #525C6C); */
        }

@media (max-width: 500px) {
  /* For mobile phones: */
  .input-h-container {
    flex-direction: column;
    }
    .logo{
    height:2rem;
    }
    #register-info{
        width: 100%;
    }
}
</style>