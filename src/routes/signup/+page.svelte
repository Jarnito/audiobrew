<script lang="ts">
    import { Input, Button, Label } from "$lib/index";
    import { page } from '$app/state';
    import { supabase } from '$lib/supabaseClient';
  
    let name = '';
    let email = '';
    let password = '';
    let confirmPassword = '';
    let error = '';

    // Optional: client-side validation before submit
    function validateForm(event: Event) {
      console.log('validateForm called');
      console.log('password:', password, 'confirmPassword:', confirmPassword);
      error = '';
      if (password !== confirmPassword) {
        console.log('Passwords do not match, preventing form submission');
        event.preventDefault();
        error = 'Passwords do not match.';
      } else {
        console.log('Passwords match, form will submit');
      }
    }

    async function signInWithGoogle() {
      try {
        const { data, error } = await supabase.auth.signInWithOAuth({
          provider: 'google',
          options: {
            redirectTo: `${window.location.origin}/auth/callback`,
            queryParams: {
              prompt: 'select_account',  // Force account selection for signup
              access_type: 'offline'     // Ensure we get refresh tokens
            }
          }
        });
        if (error) throw error;
      } catch (error: any) {
        error = error.message;
        console.error('Google sign-in error:', error);
      }
    }
</script>

{#if page.form?.success}
<div class="max-w-xl mx-auto p-7 bg-white rounded-2xl shadow-lg flex flex-col items-center h-full">
  <div class="bg-green-50 border border-green-200 text-green-600 px-4 py-3 my-6 rounded-md">
    <p class="text-sm font-medium">Check your email</p>
    <p class="text-sm mt-1">We've sent you a verification link to complete your signup.</p>
  </div>
</div>
{:else}
  
  <div class="flex items-center justify-center min-h-[calc(100vh-9rem)] px-4">
    <div class="w-full max-w-[400px] mx-auto p-7 bg-white rounded-2xl shadow-lg flex flex-col">
      <!-- Title and subtitle -->
      <h2 class="text-3xl font-bold mb-9 text-center">Create your account</h2>
      
      <form class="w-full flex flex-col" method="post" action="?/signup" on:submit={validateForm}>

      <!-- Google button -->
      <Button
      type="button"
      variant="outline"
      class="w-full h-8 flex items-center justify-center gap-2 bg-gray-50 mb-2"
      onclick={signInWithGoogle}>
      <span class="flex items-center">
        <svg class="h-3 w-3" viewBox="0 0 533.5 544.3" xmlns="http://www.w3.org/2000/svg">
          <path fill="#4285F4" d="M533.5 278.4c0-17.4-1.4-34.1-4.1-50.2H272v95h146.9c-6.4 34-25.6 62.7-54.5 82.1v68h87.8c51.4-47.3 81.3-117 81.3-194.9z"/>
          <path fill="#34A853" d="M272 544.3c73.6 0 135.4-24.5 180.5-66.5l-87.8-68c-24.4 16.4-55.4 26-92.7 26-71 0-131.2-47.9-152.7-112.3H29.3v70.9c45.5 89.8 138.6 149.9 242.7 149.9z"/>
          <path fill="#FBBC05" d="M119.3 323.5c-10.6-31.4-10.6-65.6 0-97l-90-70.1C4.1 219.1-5.3 270 2.2 320.2c7.5 50.2 32.1 96 71 131.2l90-70.1z"/>
          <path fill="#EA4335" d="M272 107.7c39.9-.6 77.6 13.6 106.8 39.7l80.1-80.1C411.8 23.6 343.6-1.5 272 0 167.9 0 74.8 60.1 29.3 149.9l90 70.1c21.5-64.4 81.7-112.3 152.7-112.3z"/>
        </svg>
      </span>
      <span>Continue with Google</span>
      </Button>
      <!-- Divider -->
      <div class="flex items-center w-full my-4">
        <div class="flex-grow border-t border-gray-200"></div>
        <span class="mx-2 text-gray-400 text-sm">Or</span>
        <div class="flex-grow border-t border-gray-200"></div>
      </div>

        <div class="flex flex-col gap-3">
          <div>
            <Label for="name" class="mb-2">Full name</Label>
            <Input id="name" name="name" type="text" placeholder="John Doe" required bind:value={name} class="h-9" />
          </div>
          <div>
            <Label for="email" class="mb-2">Email</Label>
            <Input id="email" name="email" type="email" placeholder="john.doe@example.com" required bind:value={email} class="h-9" />
          </div>
          <div>
            <Label for="password" class="mb-2">Password</Label>
            <Input id="password" name="password" type="password" placeholder="********" required bind:value={password} class="h-9" />
          </div>
          <div>
            <Label for="confirm-password" class="mb-2">Confirm password</Label>
            <Input id="confirm-password" name="confirmPassword" type="password" placeholder="********" required bind:value={confirmPassword} class="h-9" />
          </div>
        </div>
        <Button type="submit" class="w-full h-9 mt-6" variant="default">Sign up</Button>
        {#if error}
          <p class="text-red-500 text-sm mt-2 text-center">{error}</p>
        {/if}
      </form>

      <p class="mt-4 text-sm text-center text-gray-500">
        Already have an account?
        <a href="/login" class="text-black font-medium hover:underline">Log in.</a>
      </p>
    </div>
  </div>
{/if}