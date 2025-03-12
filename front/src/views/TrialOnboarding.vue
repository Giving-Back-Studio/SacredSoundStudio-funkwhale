<template>
    <div class="onboarding-container">
      <!-- Main Content -->
      <main class="onboarding-content">
        <!-- Welcome Section -->
        <section class="welcome-section">
          <h1 class="welcome-title">Welcome to the Sacred Sound Trial Launch!</h1>
          <p class="welcome-description">
            As a gift, enjoy free access to our library and concert hall.
          </p>
        </section>
  
        <!-- Coming Soon Section -->
        <section class="coming-soon-section">
          <h2 class="section-title">Coming Soon: Subscriptions</h2>
          <p class="section-description">
            For continued access to future livestreamed concerts and more:
          </p>
  
          <div class="subscription-options">
            <div class="subscription-card">
              <h3 class="subscription-title">Listener</h3>
              <p class="subscription-price">$11/month</p>
              <p class="subscription-features">
                Library, concert hall, and future livestreamed concerts.
              </p>
            </div>
  
            <div class="subscription-card">
              <h3 class="subscription-title">Student</h3>
              <p class="subscription-price">$22/month</p>
              <p class="subscription-features">
                All access, including video lessons and future livestreamed concerts.
              </p>
            </div>
          </div>
  
          <p class="additional-info">
            Plus, support artists with thanks coins and fair pay.
          </p>
        </section>
  
        <!-- Explore Section -->
        <section class="explore-section">
          <div class="explore-container">
            <router-link to="/explore" 
              class="btn btn-primary explore-btn" 
              @click="showExploreConfirmation"
            >
              Explore Sacred Sound
            </router-link>
          </div>
        </section>
      </main>
    </div>
  </template>
  
  <style scoped>
  @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700&family=Playfair+Display:wght@400;600;700&display=swap');
  
  /* Base Styles */
  * {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
  }
  
  .onboarding-container {
    font-family: 'Montserrat', sans-serif;
    color: #1c8085;
    background-color: #e5f1f2;
    min-height: 100vh;
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 20px;
  }
  
  .onboarding-content {
    max-width: 800px;
    width: 100%;
    background-color: white;
    border-radius: 12px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
    padding: 40px;
  }
  
  /* Welcome Section */
  .welcome-section {
    text-align: center;
    margin-bottom: 40px;
  }
  
  .welcome-title {
    font-family: 'Playfair Display', serif;
    font-size: 32px;
    font-weight: 700;
    color: #1c8085;
    margin-bottom: 16px;
  }
  
  .welcome-description {
    font-size: 18px;
    line-height: 1.6;
    color: #333;
  }
  
  /* Coming Soon Section */
  .coming-soon-section {
    margin-bottom: 40px;
  }
  
  .section-title {
    font-family: 'Playfair Display', serif;
    font-size: 24px;
    font-weight: 600;
    color: #1c8085;
    margin-bottom: 16px;
  }
  
  .section-description {
    font-size: 16px;
    margin-bottom: 24px;
    color: #333;
  }
  
  .subscription-options {
    display: flex;
    gap: 20px;
    margin-bottom: 24px;
    flex-wrap: wrap;
  }
  
  .subscription-card {
    flex: 1;
    min-width: 250px;
    background-color: #eef3e6;
    border-radius: 8px;
    padding: 24px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
    display: flex;
    flex-direction: column;
  }
  
  .subscription-title {
    font-family: 'Playfair Display', serif;
    font-size: 20px;
    font-weight: 600;
    margin-bottom: 8px;
    color: #1c8085;
  }
  
  .subscription-price {
    font-size: 24px;
    font-weight: 700;
    margin-bottom: 12px;
    color: #e7922f;
  }
  
  .subscription-features {
    font-size: 14px;
    line-height: 1.5;
    color: #333;
    margin-bottom: 20px;
    flex-grow: 1;
  }
  
  .additional-info {
    font-size: 16px;
    font-style: italic;
    color: #555;
    text-align: center;
    margin-top: 10px;
  }
  
  /* Explore Section */
  .explore-section {
    text-align: center;
    margin-top: 40px;
  }
  
  .explore-container {
    display: flex;
    justify-content: center;
  }
  
  .explore-btn {
    padding: 14px 40px;
    font-size: 18px;
    min-width: 220px;
  }
  
  /* Buttons */
  .btn {
    padding: 14px 20px;
    border-radius: 6px;
    font-family: 'Montserrat', sans-serif;
    font-weight: 600;
    font-size: 16px;
    cursor: pointer;
    transition: all 0.2s;
    text-align: center;
    border: none;
  }
  
  .btn-primary {
    background-color: #1c8085;
    color: #eef3e6;
  }
  
  .btn-primary:hover {
    background-color: #156569;
  }
  
  /* Modal */
  .modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-color: rgba(0, 0, 0, 0.5);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 100;
  }
  
  .modal-content {
    background-color: white;
    border-radius: 8px;
    padding: 30px;
    max-width: 500px;
    width: 90%;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  }
  
  .modal-title {
    font-family: 'Playfair Display', serif;
    font-size: 24px;
    margin-bottom: 16px;
    color: #1c8085;
  }
  
  .modal-message {
    font-size: 16px;
    line-height: 1.6;
    margin-bottom: 24px;
    color: #333;
  }
  
  /* Responsive */
  @media (max-width: 600px) {
    .onboarding-content {
      padding: 24px;
    }
    
    .welcome-title {
      font-size: 28px;
    }
    
    .welcome-description {
      font-size: 16px;
    }
    
    .subscription-options {
      flex-direction: column;
    }
  }
  </style>