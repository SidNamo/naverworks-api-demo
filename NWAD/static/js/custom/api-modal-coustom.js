//////////////////////////////////////
/////////////API List Modal - ADD////////////
//////////////////////////////////////

/******/ (() => { // webpackBootstrap
/******/ 	"use strict";
var __webpack_exports__ = {};
/*!******************************************************************!*\
  !*** ../demo14/src/js/custom/utilities/modals/create-api-key.js ***!
  \******************************************************************/


// Class definition
var ModalApiListAdd = function () {
	var submitButton;
	var cancelButton;
	var validator;
	var form;
	var modal;
	var modalEl;

	// Handle form validation and submittion
	var handleForm = function() {
		// Stepper custom navigation

		// Init form validation rules. For more info check the FormValidation plugin's official documentation:https://formvalidation.io/
		validator = FormValidation.formValidation(
			form,
			{
				fields: {
					'name': {
						validators: {
							notEmpty: {
								message: 'API 이름은 필수값입니다.'
							}
						}
					},
					'ID': {
						validators: {
							notEmpty: {
								message: 'Client ID는 필수값입니다.'
							}
						}
					},
					'secret': {
						validators: {
							notEmpty: {
								message: 'Client Secret는 필수값입니다.'
							}
						}
					},
					'account': {
						validators: {
							notEmpty: {
								message: 'Service Account는 필수값입니다.'
							}
						}
					},
					'private key': {
						validators: {
							notEmpty: {
								message: 'Private Key는 필수값입니다.'
							}
						}
					},
					'scope': {
						validators: {
							notEmpty: {
								message: 'Scope는 필수값입니다.'
							}
						}
					}
				},
				plugins: {
					trigger: new FormValidation.plugins.Trigger(),
					bootstrap: new FormValidation.plugins.Bootstrap5({
						rowSelector: '.fv-row',
                        eleInvalidClass: '',
                        eleValidClass: ''
					})
				}
			}
		);

		// Action buttons
		submitButton.addEventListener('click', function (e) {
			e.preventDefault();

			// Validate form before submit
			if (validator) {
				validator.validate().then(function (status) {
					console.log('validated!');

					if (status == 'Valid') {
						submitButton.setAttribute('data-kt-indicator', 'on');

						// Disable button to avoid multiple click 
						submitButton.disabled = true;

						setTimeout(function() {
							submitButton.removeAttribute('data-kt-indicator');

							// Enable button
							submitButton.disabled = false;
							
							Swal.fire({
								text: "새로운 API가 생성되었습니다.",
								icon: "success",
								buttonsStyling: false,
								confirmButtonText: "완료하기",
								customClass: {
									confirmButton: "btn btn-primary"
								}
							}).then(function (result) {
								if (result.isConfirmed) {
									modal.hide();
								}
							});

							//form.submit(); // Submit form
						}, 500);   						
					} else {
						// Show error popuo. For more info check the plugin's official documentation: https://sweetalert2.github.io/
						Swal.fire({
							text: "필드값을 다시 확인해주세요",
							icon: "error",
							buttonsStyling: false,
							confirmButtonText: "다시 확인하기",
							customClass: {
								confirmButton: "btn btn-primary"
							}
						});
					}
				});
			}
		});

		cancelButton.addEventListener('click', function (e) {
			e.preventDefault();

			// Show confirmation popup. For more info check the plugin's official documentation: https://sweetalert2.github.io/
			Swal.fire({
				text: "작성을 취소하시겠습니까?",
				icon: "warning",
				showCancelButton: true,
				buttonsStyling: false,
				confirmButtonText: "네 취소합니다",
				cancelButtonText: "다시 돌아가기",
				customClass: {
					confirmButton: "btn btn-primary",
					cancelButton: "btn btn-active-light"
				}
			}).then(function (result) {
				if (result.value) {
					form.reset(); // Reset form	
					modal.hide(); // Hide modal				
				} else if (result.dismiss === 'cancel') {
				}
			});
		});
	}

	return {
		// Public functions
		init: function () {
			// Elements
			modalEl = document.querySelector('#modal_api_list_add');

			if (!modalEl) {
				return;
			}

			modal = new bootstrap.Modal(modalEl);

			form = document.querySelector('#modal_api_list_add_form');
			submitButton = document.getElementById('modal_api_list_add_submit');
			cancelButton = document.getElementById('modal_api_list_add_cancel');

			handleForm();
		}
	};
}();

// On document ready
KTUtil.onDOMContentLoaded(function () {
	ModalApiListAdd.init();
});
/******/ })()
;
//# sourceMappingURL=create-api-key.js.map


//////////////////////////////////////
/////////////API List Modal////////////
//////////////////////////////////////

/******/ (() => { // webpackBootstrap
/******/ 	"use strict";
var __webpack_exports__ = {};
/*!******************************************************************!*\
  !*** ../demo14/src/js/custom/utilities/modals/create-api-key.js ***!
  \******************************************************************/


// Class definition
var ModalApiList = function () {
	var submitButton;
	var cancelButton;
	var validator;
	var form;
	var modal;
	var modalEl;

	// Handle form validation and submittion
	var handleForm = function() {
		// Stepper custom navigation

		// Init form validation rules. For more info check the FormValidation plugin's official documentation:https://formvalidation.io/
		validator = FormValidation.formValidation(
			form,
			{
				fields: {
					'name': {
						validators: {
							notEmpty: {
								message: 'API 이름은 필수값입니다.'
							}
						}
					},
					'ID': {
						validators: {
							notEmpty: {
								message: 'Client ID는 필수값입니다.'
							}
						}
					},
					'secret': {
						validators: {
							notEmpty: {
								message: 'Client Secret는 필수값입니다.'
							}
						}
					},
					'account': {
						validators: {
							notEmpty: {
								message: 'Service Account는 필수값입니다.'
							}
						}
					},
					'private key': {
						validators: {
							notEmpty: {
								message: 'Private Key는 필수값입니다.'
							}
						}
					},
					'scope': {
						validators: {
							notEmpty: {
								message: 'Scope는 필수값입니다.'
							}
						}
					}
				},
				plugins: {
					trigger: new FormValidation.plugins.Trigger(),
					bootstrap: new FormValidation.plugins.Bootstrap5({
						rowSelector: '.fv-row',
                        eleInvalidClass: '',
                        eleValidClass: ''
					})
				}
			}
		);

		// Action buttons
		submitButton.addEventListener('click', function (e) {
			e.preventDefault();

			// Validate form before submit
			if (validator) {
				validator.validate().then(function (status) {
					console.log('validated!');

					if (status == 'Valid') {
						submitButton.setAttribute('data-kt-indicator', 'on');

						// Disable button to avoid multiple click 
						submitButton.disabled = true;

						setTimeout(function() {
							submitButton.removeAttribute('data-kt-indicator');

							// Enable button
							submitButton.disabled = false;
							
							Swal.fire({
								text: "API 정보가 수정되었습니다.",
								icon: "success",
								buttonsStyling: false,
								confirmButtonText: "완료하기",
								customClass: {
									confirmButton: "btn btn-primary"
								}
							}).then(function (result) {
								if (result.isConfirmed) {
									modal.hide();
								}
							});

							//form.submit(); // Submit form
						}, 500);   						
					} else {
						// Show error popuo. For more info check the plugin's official documentation: https://sweetalert2.github.io/
						Swal.fire({
							text: "필드값을 다시 확인해주세요",
							icon: "error",
							buttonsStyling: false,
							confirmButtonText: "다시 확인하기",
							customClass: {
								confirmButton: "btn btn-primary"
							}
						});
					}
				});
			}
		});

		cancelButton.addEventListener('click', function (e) {
			e.preventDefault();

			// Show confirmation popup. For more info check the plugin's official documentation: https://sweetalert2.github.io/
			Swal.fire({
				text: "정보 변경을 취소하겠습니까?",
				icon: "warning",
				showCancelButton: true,
				buttonsStyling: false,
				confirmButtonText: "네 취소합니다",
				cancelButtonText: "다시 수정하기",
				customClass: {
					confirmButton: "btn btn-primary",
					cancelButton: "btn btn-active-light"
				}
			}).then(function (result) {
				if (result.value) {
					form.reset(); // Reset form	
					modal.hide(); // Hide modal				
				} else if (result.dismiss === 'cancel') {
				}
			});
		});
	}

	return {
		// Public functions
		init: function () {
			// Elements
			modalEl = document.querySelector('#modal-api-list');

			if (!modalEl) {
				return;
			}

			modal = new bootstrap.Modal(modalEl);

			form = document.querySelector('#modal-api-list_form');
			submitButton = document.getElementById('modal-api-list_submit');
			cancelButton = document.getElementById('modal-api-list_cancel');

			handleForm();
		}
	};
}();

// On document ready
KTUtil.onDOMContentLoaded(function () {
	ModalApiList.init();
});
/******/ })()
;
//# sourceMappingURL=create-api-key.js.map




//////////////////////////////////////
////////////Bot List Modal ADD////////////
//////////////////////////////////////

/******/ (() => { // webpackBootstrap
/******/ 	"use strict";
var __webpack_exports__ = {};
/*!************************************************************!*\
  !*** ../demo14/src/js/custom/utilities/modals/new-card.js ***!
  \************************************************************/


// Class definition
var ModalBotListAdd = function () {
	var submitButton;
	var cancelButton;
	var validator;
	var form;
	var modal;
	var modalEl;

	// Handle form validation and submittion
	var handleForm = function() {
		// Stepper custom navigation

		// Init form validation rules. For more info check the FormValidation plugin's official documentation:https://formvalidation.io/
		validator = FormValidation.formValidation(
			form,
			{
				fields: {
					'api_select': {
						validators: {
							notEmpty: {
								message: 'API를 선택해주세요.'
							}
						}
					},
					'Bot_ID': {
						validators: {
							notEmpty: {
								message: 'Bot ID는 필수값입니다.'
							}
						}
					},
					'bot_secret': {
						validators: {
							notEmpty: {
								message: 'Bot Secret는 필수값입니다'
							}
						}
					},
				},
				
				plugins: {
					trigger: new FormValidation.plugins.Trigger(),
					bootstrap: new FormValidation.plugins.Bootstrap5({
						rowSelector: '.fv-row',
                        eleInvalidClass: '',
                        eleValidClass: ''
					})
				}
			}
		);

		// Action buttons
		submitButton.addEventListener('click', function (e) {
			// Prevent default button action
			e.preventDefault();

			// Validate form before submit
			if (validator) {
				validator.validate().then(function (status) {
					console.log('validated!');

					if (status == 'Valid') {
						// Show loading indication
						submitButton.setAttribute('data-kt-indicator', 'on');

						// Disable button to avoid multiple click 
						submitButton.disabled = true;

						// Simulate form submission. For more info check the plugin's official documentation: https://sweetalert2.github.io/
						setTimeout(function() {
							// Remove loading indication
							submitButton.removeAttribute('data-kt-indicator');

							// Enable button
							submitButton.disabled = false;
							
							// Show popup confirmation 
							Swal.fire({
								text: "새로운 Bot이 생성되었습니다.",
								icon: "success",
								buttonsStyling: false,
								confirmButtonText: "완료하기",
								customClass: {
									confirmButton: "btn btn-primary"
								}
							}).then(function (result) {
								if (result.isConfirmed) {
									modal.hide();
								}
							});

							//form.submit(); // Submit form
						}, 500);   						
					} else {
						// Show popup warning. For more info check the plugin's official documentation: https://sweetalert2.github.io/
						Swal.fire({
							text: "필드값을 다시 확인해주세요",
							icon: "error",
							buttonsStyling: false,
							confirmButtonText: "다시 확인하기",
							customClass: {
								confirmButton: "btn btn-primary"
							}
						});
					}
				});
			}
		});

		cancelButton.addEventListener('click', function (e) {
			e.preventDefault();

			// Show success message. For more info check the plugin's official documentation: https://sweetalert2.github.io/
			Swal.fire({
				text: "작성을 취소하시겠습니까?",
				icon: "warning",
				showCancelButton: true,
				buttonsStyling: false,
				confirmButtonText: "네 취소합니다",
				cancelButtonText: "다시 돌아가기",
				customClass: {
					confirmButton: "btn btn-primary",
					cancelButton: "btn btn-active-light"
				}
			}).then(function (result) {
				if (result.value) {
					form.reset(); // Reset form	
					modal.hide(); // Hide modal				
				} else if (result.dismiss === 'cancel') {
				}
			});
		});
	}

	return {
		// Public functions
		init: function () {
			// Elements
			modalEl = document.querySelector('#modal_bot_list_add');

			if (!modalEl) {
				return;
			}

			modal = new bootstrap.Modal(modalEl);

			form = document.querySelector('#modal_bot_list_add_form');
			submitButton = document.getElementById('modal_bot_list_add_submit');
			cancelButton = document.getElementById('modal_bot_list_add_cancel');

			handleForm();
		}
	};
}();

// On document ready
KTUtil.onDOMContentLoaded(function () {
	ModalBotListAdd.init();
});
/******/ })()
;
//# sourceMappingURL=new-card.js.map



//////////////////////////////////////
////////////Bot List Modal////////////
//////////////////////////////////////

/******/ (() => { // webpackBootstrap
/******/ 	"use strict";
var __webpack_exports__ = {};
/*!************************************************************!*\
  !*** ../demo14/src/js/custom/utilities/modals/new-card.js ***!
  \************************************************************/


// Class definition
var ModalBotList = function () {
	var submitButton;
	var cancelButton;
	var validator;
	var form;
	var modal;
	var modalEl;

	// Handle form validation and submittion
	var handleForm = function() {
		// Stepper custom navigation

		// Init form validation rules. For more info check the FormValidation plugin's official documentation:https://formvalidation.io/
		validator = FormValidation.formValidation(
			form,
			{
				fields: {
					'api_select': {
						validators: {
							notEmpty: {
								message: 'API를 선택해주세요.'
							}
						}
					},
					'Bot_ID': {
						validators: {
							notEmpty: {
								message: 'Bot ID는 필수값입니다.'
							}
						}
					},
					'bot_secret': {
						validators: {
							notEmpty: {
								message: 'Bot Secret는 필수값입니다'
							}
						}
					},
				},
				
				plugins: {
					trigger: new FormValidation.plugins.Trigger(),
					bootstrap: new FormValidation.plugins.Bootstrap5({
						rowSelector: '.fv-row',
                        eleInvalidClass: '',
                        eleValidClass: ''
					})
				}
			}
		);

		// Action buttons
		submitButton.addEventListener('click', function (e) {
			// Prevent default button action
			e.preventDefault();

			// Validate form before submit
			if (validator) {
				validator.validate().then(function (status) {
					console.log('validated!');

					if (status == 'Valid') {
						// Show loading indication
						submitButton.setAttribute('data-kt-indicator', 'on');

						// Disable button to avoid multiple click 
						submitButton.disabled = true;

						// Simulate form submission. For more info check the plugin's official documentation: https://sweetalert2.github.io/
						setTimeout(function() {
							// Remove loading indication
							submitButton.removeAttribute('data-kt-indicator');

							// Enable button
							submitButton.disabled = false;
							
							// Show popup confirmation 
							Swal.fire({
								text: "Bot 정보가 수정되었습니다.",
								icon: "success",
								buttonsStyling: false,
								confirmButtonText: "완료하기",
								customClass: {
									confirmButton: "btn btn-primary"
								}
							}).then(function (result) {
								if (result.isConfirmed) {
									modal.hide();
								}
							});

							//form.submit(); // Submit form
						}, 500);   						
					} else {
						// Show popup warning. For more info check the plugin's official documentation: https://sweetalert2.github.io/
						Swal.fire({
							text: "필드값을 다시 확인해주세요",
							icon: "error",
							buttonsStyling: false,
							confirmButtonText: "다시 확인하기",
							customClass: {
								confirmButton: "btn btn-primary"
							}
						});
					}
				});
			}
		});

		cancelButton.addEventListener('click', function (e) {
			e.preventDefault();

			// Show success message. For more info check the plugin's official documentation: https://sweetalert2.github.io/
			Swal.fire({
				text: "정보 변경을 취소하겠습니까?",
				icon: "warning",
				showCancelButton: true,
				buttonsStyling: false,
				confirmButtonText: "네 취소합니다",
				cancelButtonText: "다시 수정하기",
				customClass: {
					confirmButton: "btn btn-primary",
					cancelButton: "btn btn-active-light"
				}
			}).then(function (result) {
				if (result.value) {
					form.reset(); // Reset form	
					modal.hide(); // Hide modal				
				} else if (result.dismiss === 'cancel') {
				}
			});
		});
	}

	return {
		// Public functions
		init: function () {
			// Elements
			modalEl = document.querySelector('#modal_bot_list');

			if (!modalEl) {
				return;
			}

			modal = new bootstrap.Modal(modalEl);

			form = document.querySelector('#modal_bot_list_form');
			submitButton = document.getElementById('modal_bot_list_submit');
			cancelButton = document.getElementById('modal_bot_list_cancel');

			handleForm();
		}
	};
}();

// On document ready
KTUtil.onDOMContentLoaded(function () {
	ModalBotList.init();
});
/******/ })()
;
//# sourceMappingURL=new-card.js.map


////// Delete Alert //////

const button = document.getElementById('delete_alert');

button.addEventListener('click', e =>{
    e.preventDefault();

    Swal.fire({
        text: "해당 정보를 삭제하시겠습니까?",
        icon: "warning",
		showCancelButton: true,
        buttonsStyling: false,
        confirmButtonText: "네 삭제합니다",
		cancelButtonText: "다시 돌아가기",
        customClass: {
            confirmButton: "btn btn-danger",
			cancelButton: "btn btn-active-light"
        }
    });
});

//////////////////////////////////////
////////////Bot Message 전달////////////
//////////////////////////////////////

/******/ (() => { // webpackBootstrap
/******/ 	"use strict";
var __webpack_exports__ = {};
/*!************************************************************!*\
  !*** ../demo14/src/js/custom/utilities/modals/new-card.js ***!
  \************************************************************/


// Class definition
var ModalBotMessageCofirm = function () {
	var submitButton;
	var cancelButton;
	var modal;
	var modalEl;

	// Handle form validation and submittion
	var handleForm = function() {
		// Stepper custom navigation

		// // Action buttons
		// submitButton.addEventListener('click', function (e) {
		// 	// Prevent default button action
		// 	e.preventDefault();

		// 	modal.hide(); // Hide modal	

		// });

		cancelButton.addEventListener('click', function (e) {
			e.preventDefault();

			modal.hide(); // Hide modal	
		});
	}

	return {
		// Public functions
		init: function () {
			// Elements
			modalEl = document.querySelector('#modal_bot_message_confirm');

			if (!modalEl) {
				return;
			}

			modal = new bootstrap.Modal(modalEl);

			submitButton = document.getElementById('modal_bot_message_confirm_submit');
			cancelButton = document.getElementById('modal_bot_message_confirm_cancel');

			handleForm();
		}
	};
}();

// On document ready
KTUtil.onDOMContentLoaded(function () {
	ModalBotMessageCofirm.init();
});
/******/ })()
;
//# sourceMappingURL=new-card.js.map
