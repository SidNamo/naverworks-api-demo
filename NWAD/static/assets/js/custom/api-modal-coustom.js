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
					'api_name': {
						validators: {
							notEmpty: {
								message: 'API 이름은 필수값입니다.'
							}
						}
					},
					'client_id': {
						validators: {
							notEmpty: {
								message: 'Client ID는 필수값입니다.'
							}
						}
					},
					'client_secret': {
						validators: {
							notEmpty: {
								message: 'Client Secret는 필수값입니다.'
							}
						}
					},
					'service_account': {
						validators: {
							notEmpty: {
								message: 'Service Account는 필수값입니다.'
							}
						}
					},
					'private_key': {
						validators: {
							notEmpty: {
								message: 'Private Key는 필수값입니다.'
							}
						}
					},
					'scope_tags': {
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
					//console.log('validated!');

					if (status == 'Valid') {
						submitButton.setAttribute('data-kt-indicator', 'on');

						// Disable button to avoid multiple click 
						submitButton.disabled = true;

						let url = "./api/apiReg";
						let formData = new FormData(form);
						formData.append("csrfmiddlewaretoken",Cookies("csrftoken"));

						let scopes = JSON.parse(form.querySelector('input[name=scope_tags]').value);
						let scope = '';
						for(let i = 0 ; i < scopes.length; i++){
							if(i != 0) scope += ',';
							scope += scopes[i].value.trim();
						}
						formData.append("scope",scope);

						
						fetch(url, {
							method: "POST",
							cache: 'no-cache',
							body: formData,
						}).then((response) => {
							if (!response.ok || response.status != '200') {
								throw new Error('연결 실패. 다시 요청하세요.\n' + response.statusText + "(" + response.status + ")");
							}
							return response.json();
						}).then((res) => {
							if(res.flag == '0'){
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
										form.reset(); // Reset form	
										modalFeedbackReset(modalEl);
									}
								});
							}else{
								throw new Error(res.result_msg);
							}
						}).catch((err) => {
							submitButton.removeAttribute('data-kt-indicator');
							// Enable button
							submitButton.disabled = false;
							Swal.fire({
								text: err,
								icon: "error",
								buttonsStyling: false,
								confirmButtonText: "확인",
								customClass: {
									confirmButton: "btn btn-primary"
								}
							});
						});
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
						}).then(e=>{
							modalTabSet();
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
					modalFeedbackReset(modalEl);		
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
					'api_name': {
						validators: {
							notEmpty: {
								message: 'API 이름은 필수값입니다.'
							}
						}
					},
					'client_id': {
						validators: {
							notEmpty: {
								message: 'Client ID는 필수값입니다.'
							}
						}
					},
					'client_secret': {
						validators: {
							notEmpty: {
								message: 'Client Secret는 필수값입니다.'
							}
						}
					},
					'service_account': {
						validators: {
							notEmpty: {
								message: 'Service Account는 필수값입니다.'
							}
						}
					},
					'private_key': {
						validators: {
							notEmpty: {
								message: 'Private Key는 필수값입니다.'
							}
						}
					},
					'scope_tags': {
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
					//console.log('validated!');

					if (status == 'Valid') {
						submitButton.setAttribute('data-kt-indicator', 'on');

						// Disable button to avoid multiple click 
						submitButton.disabled = true;

						let url = "./api/apiUpd";
						let formData = new FormData(form);

						let scopes = JSON.parse(form.querySelector('input[name=scope_tags]').value);
						let scope = '';
						for(let i = 0 ; i < scopes.length; i++){
							if(i != 0) scope += ',';
							scope += scopes[i].value.trim();
						}
						formData.append("scope",scope);

						
						fetch(url, {
							method: "POST",
							cache: 'no-cache',
							body: formData,
						}).then((response) => {
							if (!response.ok || response.status != '200') {
								throw new Error('연결 실패. 다시 요청하세요.\n' + response.statusText + "(" + response.status + ")");
							}
							return response.json();
						}).then((res) => {
							if(res.flag == '0'){
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
										form.reset(); // Reset form	
									}
								});
							}else{
								throw new Error(res.result_msg);
							}
						}).catch((err) => {
							submitButton.removeAttribute('data-kt-indicator');
							// Enable button
							submitButton.disabled = false;
							Swal.fire({
								text: err,
								icon: "error",
								buttonsStyling: false,
								confirmButtonText: "확인",
								customClass: {
									confirmButton: "btn btn-primary"
								}
							});
						});
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
/////////////Tagify script////////////
//////////////////////////////////////

// The DOM elements you wish to replace with Tagify
var input2 = document.querySelector("#kt_tagify_2");
var input3 = document.querySelector("#kt_tagify_3");

// Initialize Tagify components on the above inputs
new Tagify(input2);
new Tagify(input3);



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
					'api_no': {
						validators: {
							notEmpty: {
								message: 'API를 선택해주세요.'
							}
						}
					},
					'bot_id': {
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
					//console.log('validated!');

					if (status == 'Valid') {
						// Show loading indication
						submitButton.setAttribute('data-kt-indicator', 'on');

						// Disable button to avoid multiple click 
						submitButton.disabled = true;

						let url = "./bot/botReg";
						let formData = new FormData(form);

						
						fetch(url, {
							method: "POST",
							cache: 'no-cache',
							body: formData,
						}).then((response) => {
							if (!response.ok || response.status != '200') {
								throw new Error('연결 실패. 다시 요청하세요.\n' + response.statusText + "(" + response.status + ")");
							}
							return response.json();
						}).then((res) => {
							if(res.flag == '0'){
								submitButton.removeAttribute('data-kt-indicator');
								// Enable button
								submitButton.disabled = false;
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
										form.reset(); // Reset form	
									}
								});
							}else{
								throw new Error(res.result_msg);
							}
						}).catch((err) => {
							submitButton.removeAttribute('data-kt-indicator');
							// Enable button
							submitButton.disabled = false;
							Swal.fire({
								text: err,
								icon: "error",
								buttonsStyling: false,
								confirmButtonText: "확인",
								customClass: {
									confirmButton: "btn btn-primary"
								}
							});
						});											
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
						}).then(e=>{
							modalTabSet();
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
					'bot_name': {
						validators: {
							notEmpty: {
								message: 'Bot 이름은 필수값입니다.'
							}
						}
					},
					'api_no': {
						validators: {
							notEmpty: {
								message: 'API를 선택해주세요.'
							}
						}
					},
					'bot_id': {
						validators: {
							notEmpty: {
								message: 'Bot ID는 필수값입니다.'
							}
						}
					},
					'bot_secret': {
						validators: {
							notEmpty: {
								message: 'Bot Secret는 필수값입니다.'
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
					//console.log('validated!');

					if (status == 'Valid') {
						// Show loading indication
						submitButton.setAttribute('data-kt-indicator', 'on');

						// Disable button to avoid multiple click 
						submitButton.disabled = true;

						let url = "./bot/botUpd";
						let formData = new FormData(form);

						
						fetch(url, {
							method: "POST",
							cache: 'no-cache',
							body: formData,
						}).then((response) => {
							if (!response.ok || response.status != '200') {
								throw new Error('연결 실패. 다시 요청하세요.\n' + response.statusText + "(" + response.status + ")");
							}
							return response.json();
						}).then((res) => {
							if(res.flag == '0'){
								submitButton.removeAttribute('data-kt-indicator');
								// Enable button
								submitButton.disabled = false;
								Swal.fire({
									text: "BOT 정보가 수정되었습니다.",
									icon: "success",
									buttonsStyling: false,
									confirmButtonText: "완료하기",
									customClass: {
										confirmButton: "btn btn-primary"
									}
								}).then(function (result) {
									if (result.isConfirmed) {
										modal.hide();
										form.reset(); // Reset form	
									}
								});
							}else{
								throw new Error(res.result_msg);
							}
						}).catch((err) => {
							submitButton.removeAttribute('data-kt-indicator');
							// Enable button
							submitButton.disabled = false;
							Swal.fire({
								text: err,
								icon: "error",
								buttonsStyling: false,
								confirmButtonText: "확인",
								customClass: {
									confirmButton: "btn btn-primary"
								}
							});
						});						
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

// const button = document.getElementById('delete_alert');

// button.addEventListener('click', e =>{
//     e.preventDefault();

//     Swal.fire({
//         text: "해당 정보를 삭제하시겠습니까?",
//         icon: "warning",
// 		showCancelButton: true,
//         buttonsStyling: false,
//         confirmButtonText: "네 삭제합니다",
// 		cancelButtonText: "다시 돌아가기",
//         customClass: {
//             confirmButton: "btn btn-danger",
// 			cancelButton: "btn btn-active-light"
//         }
//     });
// });

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


//////////////////////////////////////
////////////Bot Message 전송////////////
//////////////////////////////////////

/******/ (() => { // webpackBootstrap
/******/ 	"use strict";
var __webpack_exports__ = {};
/*!******************************************************************!*\
  !*** ../demo14/src/js/custom/utilities/modals/create-api-key.js ***!
  \******************************************************************/


// Class definition
var DivBotMessageSend = function () {
	var submitButton;
	var validator;
	var form;

	// Handle form validation and submittion
	var handleForm = function() {
		// Stepper custom navigation

		// Init form validation rules. For more info check the FormValidation plugin's official documentation:https://formvalidation.io/
		validator = FormValidation.formValidation(
			form,
			{
				fields: {
					'api_no': {
						validators: {
							notEmpty: {
								message: 'API는 필수값입니다.'
							}
						}
					},
					'bot_no': {
						validators: {
							notEmpty: {
								message: 'Bot은 필수값입니다.'
							}
						}
					},
					'message_type': {
						validators: {
							notEmpty: {
								message: 'Type은 필수값입니다.'
							}
						}
					},
					'member': {
						validators: {
							notEmpty: {
								message: 'Member Id는 필수값입니다.'
							}
						}
					},
					'message': {
						validators: {
							notEmpty: {
								message: 'Message는 필수값입니다.'
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
					//console.log('validated!');

					if (status == 'Valid') {
						submitButton.setAttribute('data-kt-indicator', 'on');

						// Disable button to avoid multiple click 
						submitButton.disabled = true;

						let url = "./botMessage";
						let formData = new FormData(form);
						formData.append("csrfmiddlewaretoken",Cookies("csrftoken"));
						formData.append("type", "sendMessage");
						
						fetch(url, {
							method: "POST",
							cache: 'no-cache',
							body: formData,
						}).then((response) => {
							if (!response.ok || response.status != '200') {
								throw new Error('연결 실패. 다시 요청하세요.\n' + response.statusText + "(" + response.status + ")");
							}
							return response.json();
						}).then((res) => {
							if(res.flag == '0'){
								submitButton.removeAttribute('data-kt-indicator');
								// Enable button
								submitButton.disabled = false;
								Swal.fire({
									html: '<strong class="fs-4">전송 완료</strong><br /><span class="fs-6">메시지가 정상적으로 전송되었습니다.</span>',
									icon: "success",
									buttonsStyling: false,
									showCancelButton: false,
									confirmButtonText: '확인',
									customClass: {
										confirmButton: "btn btn-primary px-5 py-2"
									}
								});
							}else{
								throw new Error(res.result_msg);
							}
						}).catch((err) => {
							submitButton.removeAttribute('data-kt-indicator');
							// Enable button
							submitButton.disabled = false;
							Swal.fire({
								text: err,
								icon: "error",
								buttonsStyling: false,
								confirmButtonText: "확인",
								customClass: {
									confirmButton: "btn btn-primary"
								}
							});
						});
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
	}

	return {
		// Public functions
		init: function () {
			form = document.querySelector('#formBotMessageSend');
			if (!form) {
				return;
			}

			submitButton = form.querySelector('#sm_bot_msg_send');

			handleForm();
		}
	};
}();

// On document ready
KTUtil.onDOMContentLoaded(function () {
	DivBotMessageSend.init();
});
/******/ })()
;
//# sourceMappingURL=create-api-key.js.map


//////////////////////////////////////
////////////My Page Save////////////
//////////////////////////////////////

/******/ (() => { // webpackBootstrap
/******/ 	"use strict";
var __webpack_exports__ = {};
/*!******************************************************************!*\
  !*** ../demo14/src/js/custom/utilities/modals/create-api-key.js ***!
  \******************************************************************/


// Class definition
var DivMyPageSave = function () {
	var submitButton;
	var validator;
	var form;

	// Handle form validation and submittion
	var handleForm = function() {
		// Stepper custom navigation

		// Init form validation rules. For more info check the FormValidation plugin's official documentation:https://formvalidation.io/
		validator = FormValidation.formValidation(
			form,
			{
				fields: {
					'id': {
						validators: {
							notEmpty: {
								message: 'ID는 필수값입니다.'
							}
						}
					},
					'corp_name': {
						validators: {
							notEmpty: {
								message: '업체명은 필수값입니다.'
							}
						}
					},
					'name': {
						validators: {
							notEmpty: {
								message: '관리자 이름은 필수값입니다.'
							}
						}
					},
					'email': {
						validators: {
							notEmpty: {
								message: '이메일은 필수값입니다.'
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
					//console.log('validated!');

					if (status == 'Valid') {
						submitButton.setAttribute('data-kt-indicator', 'on');

						// Disable button to avoid multiple click 
						submitButton.disabled = true;

						let url = "./mypage";
						let formData = new FormData(form);
						formData.append("csrfmiddlewaretoken",Cookies("csrftoken"));
						formData.append("type", "saveInfo");
			
						fetch(url, {
							method: "POST",
							cache: 'no-cache',
							body: formData,
						}).then((response) => {
							if (!response.ok || response.status != '200') {
								throw new Error('연결 실패. 다시 요청하세요.\n' + response.statusText + "(" + response.status + ")");
							}
							return response.json();
						}).then((res) => {
							submitButton.removeAttribute('data-kt-indicator');
							// Enable button
							submitButton.disabled = false;
							if(res.flag == '0'){
								Swal.fire({
									html: '<strong class="fs-4">기본 정보 저장 완료</strong><br /><span class="fs-6">변경하신 정보가 정상적으로 저장되었습니다.</span>',
									icon: "success",
									buttonsStyling: false,
									showCancelButton: false,
									confirmButtonText: '확인',
									customClass: {
										confirmButton: "btn btn-primary px-5 py-2"
									}
								});
							}else{
								throw new Error(res.result_msg);
							}
						}).catch((err) => {
							Swal.fire({
								text: err,
								icon: "error",
								buttonsStyling: false,
								confirmButtonText: "확인",
								customClass: {
									confirmButton: "btn btn-primary"
								}
							}).then(function (result) {
								if (result.isConfirmed) {
									modalClose();
								}
							});
						});

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
	}

	return {
		// Public functions
		init: function () {
			form = document.querySelector('#formUserInfo');
			if (!form) {
				return;
			}

			submitButton = form.querySelector('#sm_myinfo_save_completed');

			handleForm();
		}
	};
}();

// On document ready
KTUtil.onDOMContentLoaded(function () {
	DivMyPageSave.init();
});
/******/ })()
;
//# sourceMappingURL=create-api-key.js.map



//////////////////////////////////////
////////////MyPage PW Modal////////////
//////////////////////////////////////

/******/ (() => { // webpackBootstrap
/******/ 	"use strict";
var __webpack_exports__ = {};
/*!************************************************************!*\
  !*** ../demo14/src/js/custom/utilities/modals/new-card.js ***!
  \************************************************************/


// Class definition
var ModalMyPagePw = function () {
	var submitButton;
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
					'current_password': {
						validators: {
							notEmpty: {
								message: '기존 비밀번호는 필수값입니다.'
							}
						}
					},
					'new_password': {
						validators: {
							notEmpty: {
								message: '새 비밀번호는 필수값입니다.'
							}
						}
					},
					'new_password_check': {
						validators: {
							notEmpty: {
								message: '새 비밀번호 확인은 필수값입니다.'
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
			// Prevent default button action
			e.preventDefault();

			// Validate form before submit
			if (validator) {
				validator.validate().then(function (status) {
					//console.log('validated!');

					if (status == 'Valid') {
						// Show loading indication
						submitButton.setAttribute('data-kt-indicator', 'on');

						// Disable button to avoid multiple click 
						submitButton.disabled = true;

						let url = "./mypage";
						let formData = new FormData(form);
						formData.append("csrfmiddlewaretoken",Cookies("csrftoken"));
						formData.append("type", "savePw");
						formData.append("current_password", form.querySelector('input[name=current_password]').value)
						formData.append("new_password", form.querySelector('input[name=new_password]').value)
						formData.append("new_password_check", form.querySelector('input[name=new_password_check]').value)
			
						fetch(url, {
							method: "POST",
							cache: 'no-cache',
							body: formData,
						}).then((response) => {
							if (!response.ok || response.status != '200') {
								throw new Error('연결 실패. 다시 요청하세요.\n' + response.statusText + "(" + response.status + ")");
							}
							return response.json();
						}).then((res) => {
							submitButton.removeAttribute('data-kt-indicator');
							// Enable button
							submitButton.disabled = false;
							if(res.flag == '0'){
								Swal.fire({
									html: '<strong class="fs-4">비밀번호 재설정 완료</strong><br /><span class="fs-6">비밀번호 변경이 정상적으로 완료되었습니다.</span>',
									icon: "success",
									buttonsStyling: false,
									showCancelButton: false,
									confirmButtonText: '확인',
									customClass: {
										confirmButton: "btn btn-primary px-5 py-2"
									}
								}).then(function(){
									location.reload();
								});
							}else{
								throw new Error(res.result_msg);
							}
						}).catch((err) => {
							Swal.fire({
								text: err,
								icon: "error",
								buttonsStyling: false,
								confirmButtonText: "확인",
								customClass: {
									confirmButton: "btn btn-primary"
								}
							}).then(function (result) {
								if (result.isConfirmed) {
									modalClose();
								}
							});
						});
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
	}

	return {
		// Public functions
		init: function () {
			// Elements
			modalEl = document.querySelector('#sm_pw_edit');

			if (!modalEl) {
				return;
			}

			modal = new bootstrap.Modal(modalEl);

			form = modalEl.querySelector('#formUserInfoPw');
			submitButton = form.querySelector('#sm_pw_edit_completed');

			handleForm();
		}
	};
}();

// On document ready
KTUtil.onDOMContentLoaded(function () {
	ModalMyPagePw.init();
});
/******/ })()
;
//# sourceMappingURL=new-card.js.map



//////////////////////////////////////
////////////My Page Withdrawal////////////
//////////////////////////////////////

/******/ (() => { // webpackBootstrap
/******/ 	"use strict";
var __webpack_exports__ = {};
/*!******************************************************************!*\
  !*** ../demo14/src/js/custom/utilities/modals/create-api-key.js ***!
  \******************************************************************/


// Class definition
var DivMyWithdrawal = function () {
	var submitButton;
	var validator;
	var form;

	// Handle form validation and submittion
	var handleForm = function() {
		// Stepper custom navigation

		// Init form validation rules. For more info check the FormValidation plugin's official documentation:https://formvalidation.io/
		validator = FormValidation.formValidation(
			form,
			{
				fields: {
					'current_password': {
						validators: {
							notEmpty: {
								message: '비밀번호는 필수입니다.'
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
			e.preventDefault();

			// Validate form before submit
			if (validator) {
				validator.validate().then(function (status) {
					//console.log('validated!');

					if (status == 'Valid') {
						submitButton.setAttribute('data-kt-indicator', 'on');

						// Disable button to avoid multiple click 
						submitButton.disabled = true;

						let url = "./withdrawal";
						let formData = new FormData(form);
						formData.append("csrfmiddlewaretoken",Cookies("csrftoken"));
			
						fetch(url, {
							method: "POST",
							cache: 'no-cache',
							body: formData,
						}).then((response) => {
							if (!response.ok || response.status != '200') {
								throw new Error('연결 실패. 다시 요청하세요.\n' + response.statusText + "(" + response.status + ")");
							}
							return response.json();
						}).then((res) => {
							submitButton.removeAttribute('data-kt-indicator');
							// Enable button
							submitButton.disabled = false;
							if(res.flag == '0'){
								Swal.fire({
									html: '<strong class="fs-4">회원 탈퇴가 완료되었습니다.</strong>',
									icon: "success",
									buttonsStyling: false,
									showCancelButton: false,
									confirmButtonText: '확인',
									customClass: {
										confirmButton: "btn btn-primary px-5 py-2"
									}
								}).then(e=>{
									location.href = "/";
								});
							}else{
								throw new Error(res.result_msg);
							}
						}).catch((err) => {
							Swal.fire({
								text: err,
								icon: "error",
								buttonsStyling: false,
								confirmButtonText: "확인",
								customClass: {
									confirmButton: "btn btn-primary"
								}
							});
						});

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
	}

	return {
		// Public functions
		init: function () {
			form = document.querySelector('#formUserInfoWithdrawal');
			if (!form) {
				return;
			}

			submitButton = form.querySelector('#sm_withdrawal_completed');

			handleForm();
		}
	};
}();

// On document ready
KTUtil.onDOMContentLoaded(function () {
	DivMyWithdrawal.init();
});
/******/ })()
;
//# sourceMappingURL=create-api-key.js.map



//////////////////////////////////////
////////////Scenario Edit Modal////////////
//////////////////////////////////////

/******/ (() => { // webpackBootstrap
/******/ 	"use strict";
var __webpack_exports__ = {};
/*!************************************************************!*\
  !*** ../demo14/src/js/custom/utilities/modals/new-card.js ***!
  \************************************************************/


// Class definition
var ModalScenarioEdit = function () {
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
					'scen_type': {
						validators: {
							notEmpty: {
								message: 'Scenario Template은 필수값입니다.'
							}
						}
					},
					'scen_name': {
						validators: {
							notEmpty: {
								message: 'Scenario Name은 필수값입니다.'
							}
						}
					},
					'domain': {
						validators: {
							notEmpty: {
								message: 'Domain Id는 필수값입니다.'
							}
						}
					},
					'api_no': {
						validators: {
							notEmpty: {
								message: 'API는 필수값입니다.'
							}
						}
					},
					'bot_no': {
						validators: {
							notEmpty: {
								message: 'Bot은 필수값입니다.'
							}
						}
					},
					'members': {
						validators: {
							notEmpty: {
								message: 'Member는 필수값입니다.'
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
					//console.log('validated!');

					if (status == 'Valid') {
						submitButton.setAttribute('data-kt-indicator', 'on');
						// Disable button to avoid multiple click 
						submitButton.disabled = true;

						// submitButton.removeAttribute('data-kt-indicator');
						// // Enable button
						// submitButton.disabled = false;

						let url = "./scenarioList";
						let formData = new FormData(form);
						formData.append("csrfmiddlewaretoken", Cookies("csrftoken"));
						formData.append("type", "updScen");
				
				
						fetch(url, {
							method: "POST",
							cache: 'no-cache',
							body: formData,
						}).then((response) => {
							if (!response.ok || response.status != '200') {
								throw new Error('연결 실패. 다시 요청하세요.\n' + response.statusText + "(" + response.status + ")");
							}
							return response.json();
						}).then((res) => {
							submitButton.removeAttribute('data-kt-indicator');
							// Enable button
							submitButton.disabled = false;
							if(res.flag == 0){
								Swal.fire({
									html: `<strong class="fs-4">Scenario 정보 수정 확인</strong><br /><span class="fs-6">Scenario 정보 수정이 정상적으로 완료되었습니다.</span>`,
									icon: "success",
									buttonsStyling: false,
									confirmButtonText: "확인",
									customClass: {
										confirmButton: "btn btn-primary px-5 py-2",
									}
								}).then(e=>{
									getScenarioList(document.querySelector("#ulPage li.active a").dataset.selectedPage);
									modal.hide(); // Hide modal		
									modalEl.querySelector('#divMembers').innerHTML = "";		
									form.reset(); // Reset f
								});
							}else{
								throw new Error(res.result_msg);
							}
						}).catch((err) => {
							Swal.fire({
								text: err,
								icon: "error",
								buttonsStyling: false,
								confirmButtonText: "확인",
								customClass: {
									confirmButton: "btn btn-primary"
								}
							});
						});
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
					modal.hide(); // Hide modal		
					modalEl.querySelector('#divMembers').innerHTML = "";		
					form.reset(); // Reset f		
				} else if (result.dismiss === 'cancel') {
				}
			});
		});
	}

	return {
		// Public functions
		init: function () {
			// Elements
			modalEl = document.querySelector('#sm_sc_edit');

			if (!modalEl) {
				return;
			}

			modal = new bootstrap.Modal(modalEl);

			form = modalEl.querySelector('#sm_sc_edit_form');
			submitButton = modalEl.querySelector('#sm_sc_info_edit_submit');
			cancelButton = modalEl.querySelector('#sm_sc_info_edit_cancle');

			handleForm();
		}
	};
}();

// On document ready
KTUtil.onDOMContentLoaded(function () {
	ModalScenarioEdit.init();
});
/******/ })()
;
//# sourceMappingURL=create-api-key.js.map
