import { createRouter, createWebHistory } from 'vue-router';
import HomeView from '../views/HomeView.vue';
import LoginView from '../views/LoginView.vue';
import RegisterView from '../views/RegisterView.vue';
import ProjectView from '../views/ProjectView.vue';
import WelcomeView from '../views/WelcomeView.vue';
import ImpressumView from '../views/ImpressumView.vue';
import TermsAndConditionsView from '../views/TermsAndConditionsView.vue';
import CookiePolicy from '../views/CookiePolicyView.vue';


const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
      meta: {
        requiresAuth: true // Add meta field to indicate protected route
      },
      children: [
        {
          path: '/projects/:id',
          name: 'project',
          component: ProjectView,
          meta: {
            requiresAuth: true // Add meta field to indicate protected route
          },
        },
        {
          path: '/welcome',
          name: 'welcome',
          component: WelcomeView,
          meta: {
            requiresAuth: true // Add meta field to indicate protected route
          }
        },
      ],
    },
    {
      path: '/login',
      name: 'login',
      component: LoginView
    },
    {
      path: '/register',
      name: 'register',
      component: RegisterView
    },
    {
      path: '/impressum',
      name: 'impressum',
      component: ImpressumView
    },
    {
      path: '/terms-and-conditions',
      name: 'termsAndConditions',
      component: TermsAndConditionsView
    },
    {
      path: '/cookie-policy',
      name: 'cookiePolicy',
      component: CookiePolicy
    },
  ]
})

router.beforeEach((to, from, next) => {
  console.log(`Navigating from ${from.fullPath} to ${to.name}`);
  if (to.meta.requiresAuth) {
    const token = window.sessionStorage.getItem('chek_access_token');
    if (token) {
      // User is authenticated, proceed to the route
      if(to.name == "home"){
        next({ name: 'welcome' });
      }else{
        if (to.name === 'project') {
          const sidebar = document.getElementById("sidebar");
          if(sidebar && !sidebar.classList.contains("collapsed")){
              setTimeout(() => {
                sidebar.classList.add("collapsed");
              }, 500);
              
          }
        }
        next();
      }
    } else {
      // User is not authenticated, redirect to login
      next({ name: 'login' });
    }
  } else {
    // Non-protected route, allow access
    next();
  }
});


export default router
