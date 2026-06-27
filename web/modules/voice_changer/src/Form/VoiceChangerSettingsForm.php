<?php

namespace Drupal\voice_changer\Form;

use Drupal\Core\Form\ConfigFormBase;
use Drupal\Core\Form\FormStateInterface;

/**
 * Settings form for Voice Changer Python backend URL.
 */
class VoiceChangerSettingsForm extends ConfigFormBase {

  /**
   * {@inheritdoc}
   */
  public function getFormId() {
    return 'voice_changer_settings';
  }

  /**
   * {@inheritdoc}
   */
  protected function getEditableConfigNames() {
    return [];
  }

  /**
   * {@inheritdoc}
   */
  public function buildForm(array $form, FormStateInterface $form_state) {
    $api_base = \Drupal::state()->get('voice_changer.api_base', 'http://localhost:8000');

    $form['api_base'] = [
      '#type' => 'url',
      '#title' => $this->t('Python Backend URL'),
      '#description' => $this->t('Base URL for the Python voice changer API (e.g. http://localhost:8000).'),
      '#default_value' => $api_base,
      '#required' => TRUE,
    ];

    return parent::buildForm($form, $form_state);
  }

  /**
   * {@inheritdoc}
   */
  public function submitForm(array &$form, FormStateInterface $form_state) {
    \Drupal::state()->set('voice_changer.api_base', $form_state->getValue('api_base'));
    parent::submitForm($form, $form_state);
  }

}
