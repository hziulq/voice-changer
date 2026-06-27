<?php

namespace Drupal\voice_changer\Controller;

use Drupal\Core\Controller\ControllerBase;

/**
 * Controller for the Voice Changer control panel page.
 */
class VoiceChangerController extends ControllerBase {

  /**
   * Renders the Voice Changer control panel.
   */
  public function panel() {
    $api_base = \Drupal::state()->get('voice_changer.api_base', 'http://localhost:8000');
    return [
      '#theme' => 'voice_changer_control',
      '#api_base' => $api_base,
    ];
  }

}
