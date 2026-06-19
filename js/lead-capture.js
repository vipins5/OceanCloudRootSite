/**
 * Lead Capture Frontend Client
 * Communicates with OceanCloud Lead Capture Backend
 */

const LeadCapture = {
  // Configuration
  apiBaseUrl: window.location.hostname === 'localhost' 
    ? 'http://localhost:5000' 
    : `https://${window.location.hostname}/api`,
  
  /**
   * Submit lead magnet form
   */
  submitLeadForm: async function(formData) {
    try {
      const response = await fetch(`${this.apiBaseUrl}/api/lead-capture`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Requested-With': 'XMLHttpRequest'
        },
        body: JSON.stringify(formData)
      });
      
      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.error || 'Failed to capture lead');
      }
      
      return {
        success: true,
        ...data
      };
    } catch (error) {
      console.error('Lead capture error:', error);
      return {
        success: false,
        error: error.message
      };
    }
  },

  /**
   * Submit contact form (also captures as lead)
   */
  submitContactForm: async function(formData) {
    try {
      const response = await fetch(`${this.apiBaseUrl}/api/contact-submit`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Requested-With': 'XMLHttpRequest'
        },
        body: JSON.stringify(formData)
      });
      
      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.error || 'Failed to submit contact form');
      }
      
      return {
        success: true,
        ...data
      };
    } catch (error) {
      console.error('Contact form error:', error);
      return {
        success: false,
        error: error.message
      };
    }
  },

  /**
   * Get current page's lead magnet ID from URL
   */
  getMagnetIdFromUrl: function() {
    const filename = window.location.pathname.split('/').pop();
    return filename.replace(/\.html$/, '');
  },

  /**
   * Get lead magnet metadata from page attributes or meta tags
   */
  getMagnetMetadata: function() {
    const metaTitle = document.querySelector('meta[name="magnet-title"]')?.content 
      || document.querySelector('title')?.textContent?.split(' - ')[0] 
      || 'Resource';
    const metaLink = document.querySelector('meta[name="magnet-link"]')?.content 
      || window.location.pathname;
    
    return {
      magnet_id: this.getMagnetIdFromUrl(),
      magnet_title: metaTitle,
      magnet_link: metaLink
    };
  }
};

// Export for use in browser
if (typeof module !== 'undefined' && module.exports) {
  module.exports = LeadCapture;
}
