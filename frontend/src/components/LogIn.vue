<template>
    <div id="login-container">
        <div id="login-header">
            <div class="main-heading">
                CHEK
            </div>
            <div class="hd-smaller main-heading">
                Change Management Assistant
            </div>
            <div class="sub-heading">
                Log in to start improving your Building Permit process.
            </div>
        </div>
        <form id="user-info" @submit.prevent="userLogin">
            <div class="login-field">
                <div id="mail-icon"></div>
                <input id="username-input" class="login-user-input" type="text" placeholder="e-mail">
            </div>
            <div class="login-field">
                <div id="lock-icon"></div>
                <input id="password-input" class="login-user-input" type="password" placeholder="password" autocomplete="off">
            </div>

            <button type="submit" id="login-btn" class="login-field login-btn">
                <div v-if="loading" class="load-btn"></div>
                <span>{{btn_text}}</span> 
            </button>
        </form>
        <div id="registration-container">
            <div class="minor-label">
                Don't have an account?
            </div>
            <RouterLink class="minor-label link" to="/register">Register here</RouterLink>
        </div>
        <div class="logos-footer">
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
    import { useRouter } from 'vue-router';
    import { inject,onBeforeUnmount, ref, onMounted} from "vue";

    import useReCaptcha from '../composables/useReCaptcha';
    const { token, executeRecaptcha } = useReCaptcha();
    const action = 'chek_login'; // Define your action name here

    const router = useRouter();
    const base_api = inject('base_api');
    const login_api = base_api + "/login";
    const user_info_api = base_api + "/me/";
    const loading = ref(false);

    let login_btn, saved_text;

    const btn_text = ref('Login')
 

    onMounted(()=>{
        login_btn = document.getElementById('login-btn');
        saved_text = btn_text.value;
    })

    onBeforeUnmount(()=>{
        console.log('LogIN unmount!');
    });

    async function userLogin(){
        const username = document.getElementById("username-input");
        const password = document.getElementById("password-input");

        if(username.value == ""){
            username.parentElement.classList.toggle('alert-input');
            setTimeout(() => {
                username.parentElement.classList.toggle('alert-input');
                }, 2000);
            return;
        }
        if(password.value == ""){
            password.parentElement.classList.toggle('alert-input');
            setTimeout(() => {
                password.parentElement.classList.toggle('alert-input');
                }, 2000);
            return;
        }

        await executeRecaptcha(action); // Ensure reCAPTCHA token is retrieved before submission

        login_btn.disabled = true;
        loading.value = true;
        const user_credetials = new URLSearchParams();
        user_credetials.set("username", username.value);
        user_credetials.set("password", password.value);
        user_credetials.set("recaptcha_token", token.value);
        
        fetch(login_api, {
                    method: 'POST',
                    credentials: 'same-origin',
                    headers: {'Content-Type': 'application/x-www-form-urlencoded'},
                    body: user_credetials.toString(),
        })
        .then(login_response =>{
            if(login_response.ok){
                login_response.json()
                .then(access => {
                    // console.log(access);
                    window.sessionStorage.setItem('chek_access_token', access.access_token);

                    fetch(user_info_api, {
                        method: 'GET',
                        credentials: 'same-origin',
                        headers: {'Content-Type': 'application/json',
                                    'Authorization': `Bearer ${access.access_token}`}
                    })
                    .then(user_info =>{
                        user_info.json()
                        .then(user_info_data =>{
                            console.log(user_info_data);
                            window.sessionStorage.setItem('chek_user_info', JSON.stringify(user_info_data));
                            username.value = "";
                            password.value = "";
                            loading.value = false;
                            router.push("/welcome");
                        })
                        .catch(error =>{
                            console.log(error);
                            showFail();
                        });
                    })
                    .catch(error =>{
                        console.log(error);
                        showFail();
                    })
                })
                .catch(error =>{
                    console.log(error);
                    showFail();
                })
            }
            else{
                showFail();
            }
        })
        .catch(error =>{
            console.log(error);
            showFail();
        })
        

    }

    function showFail(){
        loading.value = false;
        login_btn.classList.toggle('fail-btn');
            btn_text.value = "Login failed";
                setTimeout(() => {
                    login_btn.classList.toggle('fail-btn');
                    btn_text.value = saved_text;
                    login_btn.disabled = false;
                }, 2000);
    }
</script>

<style>
    #login-container{
        grid-row-start: 1;
        grid-row-end: -1;
        grid-column-start: 1;
        grid-column-end: -1;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        gap: 2rem;
        align-items: center;
        z-index: 1;
        padding: 3rem;
    }
        #login-header{
            display: flex;
            flex-direction: column;
            gap: 1rem;
        }
            .main-heading{
                color: var(--brand-500, var(--heisenberg-blue-500, #82DBF7));
                text-align: center;
                font-feature-settings: 'liga' off;
                /* Heading XL/Bold */
                font-family: Montserrat;
                font-size: 3.75rem;
                font-style: normal;
                font-weight: 700;
                line-height: 4.5rem; /* 120% */
                letter-spacing: -0.075rem;
            }
            .hd-smaller{
                font-size: 3rem;
                line-height: 3.75rem;
                letter-spacing: -0.06rem;
            }
            .sub-heading{
                color: var(--noble-black-300, #9B9C9E);
                text-align: center;
                /* Body/XL/Medium */
                font-family: Plus Jakarta Sans;
                font-size: 1.125rem;
                font-style: normal;
                font-weight: 500;
                line-height: 1.75rem; /* 155.556% */
                letter-spacing: 0.00938rem;
            }
        #user-info{
            display: flex;
            flex-direction: column;
            justify-content: center;
            min-width: 25vw;
            gap: 1rem;
    
        }
            .login-field{
                display: flex;
                flex-direction: row;
                /* height: 3rem; */
                align-items: center;
                gap: 1rem;
                border-radius: var(--input-l, 0.625rem);
                border: 1px solid var(--neutral-100, #DCDEE2);
                background: var(--neutral-0, #FFF);
                padding: 0.75rem 1rem;
            }
            #mail-icon{
                width: 1.25rem;
                height: 1.25rem;
                background: center / contain no-repeat url(images/mail.svg);;
            }
            #lock-icon{
                width: 1.25rem;
                height: 1.25rem;
                background: center / contain no-repeat url(images/lock.svg);;
            }
            .login-user-input{
                color: var(--neutral-600, #525C6C);
                outline: none;
                border: none;
                font-feature-settings: 'case' on, 'liga' off;
                /* Input/L */
                font-family: Arial, Helvetica, sans-serif;
                font-size: 1rem;
                font-style: normal;
                font-weight: 600;
                line-height: normal;
                width: 100%;
            }
            .alert-input{
                    border: 2px solid var(--error--700);
                }
            .login-btn{
                border-radius: var(--button-l, 0.75rem);
                background: var(--brand-600, #65BEDA);
                color: #f3f3f3;
                /* outline: none;
                border: none; */
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
            .fail-btn{
                background: var(--red-power-600, #d0302f);
                color: #f3f3f3;
            }

        #registration-container{
            display: flex;
            flex-direction: row;
            justify-content: center;
            z-index: 1;
            gap:0.5rem;
        }
            .minor-label{
                color: var(--noble-black-400, #686B6E);
                font-feature-settings: 'liga' off;
                /* Paragraph L/Medium */
                font-family: MyriadPro;
                font-size: 1.125rem;
                font-style: normal;
                font-weight: 400;
                line-height: 1.75rem; /* 155.556% */
            }
            .link{
                color: var(--heisenberg-blue-500, #82DBF7);
            }
        .logos-footer{
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
</style>