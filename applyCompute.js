import { d as defineComponent, B as useI18n, C as useRouter, r as ref, az as reactive, D as useStore, c as computed, x as watch, a as onUnmounted, cJ as useRoute, o as onMounted, e as createElementBlock, f as openBlock, X as withDirectives, m as createVNode, c0 as vLoading, g as createBaseVNode, k as createBlock, u as unref, y as toDisplayString, F as Fragment, q as withCtx, aK as ElInput, E as createTextVNode, L as ElButton, b3 as Message, cD as setItem, ei as LOCALE_BEFORE_LOGIN_KEY, _ as _export_sfc } from "./index-DkDlcA9e.js";
/* empty css                 */
import { a as ElFormItem, E as ElForm } from "./form-item-DiT7dSMy.js";
import { _ as _sfc_main$2 } from "./SvgIcon.vue_vue_type_style_index_0_lang-D3HKASS0.js";
import { r as resourceRequestsAPI, b as getUserTeamsAPI, a as getTeamsMembersAPI, c as getTeamApplicationsAPI } from "./computingRequest-CUxQLpVj.js";
import { U as Upload } from "./Upload-Bcvw8nUO.js";
import { C as CustomDialog } from "./CustomDialog-0GoCmgtp.js";
import SubmissionPrCheck from "./SubmissionPrCheck-61pE2UBG.js";
import { a as formatterDateByLocale } from "./time-BFj6gshD.js";
import { C as ComputingRequestStatusEnum, b as RaceScheduleStatusEnum } from "./status-B-JY-yK6.js";
import ComputingRequestResult from "./computeResult-PzdQNVSX.js";
import { u as useInjectRaceContextSafe } from "./useRaceContext-DPWqW3nm.js";
import { w as whitelistCheck, r as rankList, _ as _sfc_main$1 } from "./whitelistCheck-DGSmoqDt.js";
import "./_baseClone-_meqkcgt.js";
import "./text-4_XEG8_I.js";
import "./dialog-CMWmpJJZ.js";
import "./index-Cy1SCpqi.js";
import "./vnode-BjE1m57K.js";
import "./scroll-C-IMOUFz.js";
import "./overlay-CgzqqYJV.js";
import "./zh-cn-Ckp6KZ3o.js";
import "./request-unstarted-DQ38zznE.js";
import "./end-CflttNIL.js";
import "./Icon-mrqshprH.js";
const _hoisted_1 = { class: "rounded-20px p-30 mb-40 overflow-hidden" };
const _hoisted_2 = { class: "race-detail-progress w-full mt--6" };
const _hoisted_3 = { class: "color-#666 text-12 text-right mt-16" };
const _hoisted_4 = {
  key: 0,
  class: "flex items-start gap-4 bg-[rgba(30,100,250,0.05)] rounded-[8px] border border-solid border-[#1E64FA] py-[10px] px-[16px] font-400 text-[14px] text-[#1E64FA] lh-20 mt-16"
};
const _hoisted_5 = {
  key: 1,
  class: "flex items-start gap-4 bg-[rgba(30,100,250,0.05)] rounded-[8px] border border-solid border-[#1E64FA] py-[10px] px-[16px] font-400 text-[14px] text-[#1E64FA] leading-[20px] mt-16"
};
const _hoisted_6 = { class: "list-disc list-inside" };
const _hoisted_7 = { class: "ml-20 list-disc list-outside" };
const _hoisted_8 = { class: "ml-20 list-disc list-outside" };
const _hoisted_9 = { class: "lh-22 text-14 color-#666 mt-16" };
const trackName = "track2";
const _sfc_main = /* @__PURE__ */ defineComponent({
  __name: "applyCompute",
  props: {
    raceDetail: {}
  },
  emits: ["changeTab"],
  setup(__props) {
    var _a, _b;
    whitelistCheck();
    const { t, locale } = useI18n();
    const router = useRouter();
    const rid = __props.raceDetail.rid;
    const pageLoading = ref(false);
    const formRef = ref(null);
    const form = reactive({
      team_id: "",
      team_name: "",
      team_users: "",
      files: []
    });
    const rules = {
      files: [{ required: true, message: t("computingRequest.filesRequired"), type: "array", trigger: "change" }]
    };
    const formDisabled = ref(false);
    const raceContext = useInjectRaceContextSafe();
    const { userState } = useStore("user");
    const resultStatus = ref(ComputingRequestStatusEnum.UNSTARTED);
    const submit = () => {
      var _a2;
      (_a2 = formRef == null ? void 0 : formRef.value) == null ? void 0 : _a2.validate(async (valid) => {
        var _a3;
        if (!valid) {
          return;
        }
        const data = {
          team_id: form.team_id,
          content_url: form.files[0].url
        };
        try {
          const res = await resourceRequestsAPI(data);
          if (res.code === 200) {
            Message.success(t("computingRequest.submitSuccess"));
            resultStatus.value = ComputingRequestStatusEnum.PENDING;
            schedulesTime.value = (_a3 = getComputeSchedule()) == null ? void 0 : _a3.time_display;
          }
        } catch (e) {
        }
      });
    };
    const reset = () => {
      var _a2;
      (_a2 = formRef.value) == null ? void 0 : _a2.resetFields();
    };
    const validateFileName = (file) => {
      const fileName = String((file == null ? void 0 : file.name) ?? file ?? "").trim();
      const teamName = String(form.team_name ?? "").trim();
      if (!teamName) return void 0;
      const ruleName = t("s2Track2.apply.applicationFileNameRule", { teamName, accept: "pdf" });
      if (fileName.toLowerCase() !== ruleName.toLowerCase()) {
        return t("s2Track2.apply.applicationFileNameRuleError");
      }
      return void 0;
    };
    const remainingSeconds = ref(0);
    computed(() => {
      const totalSeconds = remainingSeconds.value;
      if (totalSeconds <= 0) {
        return t("computingRequest.countdownZero");
      }
      const days = Math.floor(totalSeconds / 86400);
      const hours = Math.floor(totalSeconds % 86400 / 3600);
      const minutes = Math.floor(totalSeconds % 3600 / 60);
      const seconds = totalSeconds % 60;
      return t("s2Track2.countdownFormat", { days, hours, minutes, seconds });
    });
    let timer = null;
    const startCountdown = () => {
      if (timer) return;
      timer = window.setInterval(() => {
        if (remainingSeconds.value > 0) {
          remainingSeconds.value--;
        } else {
          stopCountdown();
        }
      }, 1e3);
    };
    const stopCountdown = () => {
      if (timer) {
        clearInterval(timer);
        timer = null;
      }
    };
    watch(
      () => resultStatus.value,
      (val) => {
        if (val === ComputingRequestStatusEnum.APPROVED) {
          stopCountdown();
          remainingSeconds.value = phaseTine.value || 0;
          startCountdown();
        } else {
          stopCountdown();
        }
      },
      { immediate: true }
    );
    onUnmounted(stopCountdown);
    const goLeaderboard = () => raceContext == null ? void 0 : raceContext.goTab("ranking");
    const resetSubmit = () => {
      resultStatus.value = ComputingRequestStatusEnum.APPLY;
    };
    const currentState = computed(() => {
      const status = resultStatus.value;
      let state = { status, visible: false, desc: [] };
      const resourceApplyStartTime = () => {
        var _a2;
        const startTime = (_a2 = getScheduleByCode("resource_apply")) == null ? void 0 : _a2.start_time;
        return startTime ? formatterDateByLocale(startTime, locale.value === "en" ? "en" : "zh-CN", locale.value === "en" ? "MMM DD, YYYY" : "YYYY年MM月DD日") : "";
      };
      switch (status) {
        case ComputingRequestStatusEnum.UNSTARTED:
          state = {
            status,
            visible: true,
            icon: "UNSTARTED",
            iconClass: "mt-29",
            desc: [
              {
                parts: [
                  { text: t("s2Track2.unstartedPrefix") },
                  { text: `${resourceApplyStartTime()}`, type: "highlight" },
                  { text: t("computingRequest.unstartedSuffix") },
                  { text: t("computingRequest.unstartedThanks") }
                ]
              }
            ]
          };
          break;
        case ComputingRequestStatusEnum.PENDING:
          state = {
            status,
            visible: true,
            icon: "PENDING",
            title: t("computingRequest.pendingTitle"),
            desc: [
              {
                parts: [
                  { text: t("s2Track2.apply.pendingDesc1") },
                  { text: t("s2Track2.apply.reviewDays"), type: "highlight" },
                  { text: t("s2Track2.apply.pendingDesc2") }
                ]
              },
              {
                parts: [
                  { text: t("s2Track2.apply.updateBeforeResultTip") }
                ]
              }
            ],
            action: { text: t("s2Track2.apply.resubmitAction"), handler: resetSubmit }
          };
          break;
        case ComputingRequestStatusEnum.APPROVED:
          state = {
            status,
            visible: true,
            icon: "SUBMITSUCCESS",
            title: t("s2Track2.apply.approvedTitle"),
            desc: [
              {
                parts: [
                  { text: t("s2Track2.allocatedComputeTip") }
                ]
              }
            ]
            // action: { text: t('s2Track2.goToLab'), handler: goLab }
          };
          break;
        case ComputingRequestStatusEnum.REJECTED:
          state = {
            status,
            visible: true,
            icon: "REJECTED",
            title: t("s2Track2.apply.rejectedTitle"),
            desc: [
              {
                parts: [
                  { text: t("s2Track2.apply.rejectedDesc") }
                ]
              }
            ]
          };
          if (resource_apply_rejected_count.value <= 1) {
            state = {
              ...state,
              desc: [
                {
                  parts: [
                    { text: t("s2Track2.apply.reviseTip") + t("s2Track2.apply.resubmitRemaining", { count: 1 }) }
                  ]
                },
                // {
                //     parts: [
                //         { text: t('s2Track2.apply.reviseTip') }
                //     ]
                // },
                // 评审意见：接口返回意见内容时在两句提示中间展示卡片
                ...reviewComment.value ? [
                  {
                    type: "review",
                    parts: [
                      { text: t("s2Track2.apply.reviewComments") },
                      { text: reviewComment.value }
                    ]
                  }
                ] : []
              ],
              action: { text: t("s2Track2.apply.reviseAndResubmit"), handler: resetSubmit }
            };
          }
          break;
        case ComputingRequestStatusEnum.CLOSED:
          state = {
            status,
            visible: true,
            icon: "CLOSED",
            iconClass: "mt-12",
            title: t("s2Track2.apply.closedTitle"),
            desc: [
              {
                parts: [
                  { text: t("s2Track2.apply.closedDesc") }
                ]
              }
            ]
          };
          break;
        case ComputingRequestStatusEnum.COMPETITION_CLOSED:
          state = {
            status,
            visible: true,
            icon: "END",
            desc: [
              {
                parts: [
                  { text: t("PrLink.prLimitClosedPrefix") },
                  { text: t("PrLink.prLimitClosedLeaderboard"), type: "link", handler: goLeaderboard },
                  { text: t("PrLink.prLimitClosedSuffix") }
                ]
              }
            ]
          };
          break;
        case ComputingRequestStatusEnum.COMPETITION_WINDOW_CLOSED:
          state = {
            status,
            visible: true,
            icon: "END",
            desc: [{ parts: [{ text: t("computingRequest.competitionWindowClosedTip") }] }]
          };
          break;
        case ComputingRequestStatusEnum.APPLY:
      }
      return state;
    });
    const { query = {} } = useRoute() || {};
    const raceSchedulesList = ref([]);
    raceSchedulesList.value = ((_b = (_a = raceContext == null ? void 0 : raceContext.data) == null ? void 0 : _a.raceSchedulesList) == null ? void 0 : _b.value) || [];
    const getScheduleByCode = (code) => (raceSchedulesList.value || []).find((item) => (item == null ? void 0 : item.code) === code);
    const phaseTine = ref();
    const schedulesTime = ref();
    const getComputeSchedule = () => getScheduleByCode("resource_apply");
    const isLogin = computed(() => !!userState.value.username);
    const needRegister = ref(false);
    const conflictName = ref("");
    const prChecks = computed(() => {
      let checks = [];
      switch (true) {
        case !isLogin.value:
          checks = [{ type: "login", text: t("bountyHunter.nologinPromptContent"), buttonText: t("operatorCard.goToLogin") }];
          break;
        case needRegister.value:
          checks = [{
            type: "register",
            text: t("s2Track1.dialogContent", { phone: userState.value.username, title: __props.raceDetail.title }),
            buttonText: t("computingRequest.goToRegister")
          }];
          break;
        case !!conflictName.value:
          checks = [{ type: "conflict", text: t("computingRequest.dialogContent2", { title: conflictName.value }) }];
          break;
      }
      return checks;
    });
    const hasResourceInstance = ref(false);
    const resource_apply_rejected_count = ref(0);
    const reviewComment = ref("");
    const getUserTeams = async () => {
      var _a2, _b2, _c, _d, _e, _f;
      try {
        conflictName.value = "";
        const res = await getUserTeamsAPI({ rid: query.id });
        if (!((_a2 = res.data) == null ? void 0 : _a2.length)) {
          needRegister.value = true;
          return;
        }
        const {
          rid: rid2,
          race_info: { name: rname },
          has_resource_instance
        } = ((_b2 = res.data) == null ? void 0 : _b2[0]) || { race_info: { name: "" } };
        if (rid2 !== query.id) {
          conflictName.value = (_d = (_c = res.data[0]) == null ? void 0 : _c.race_info) == null ? void 0 : _d.name;
          showDialog({
            content: t("computingRequest.dialogContent2", { title: rname }),
            confirmText: t("computingRequest.iKnow"),
            hideCancelButton: true,
            confirmCallback: () => {
            }
          });
          return;
        }
        hasResourceInstance.value = has_resource_instance;
        form.team_name = (_e = res.data[0]) == null ? void 0 : _e.name;
        form.team_id = (_f = res.data[0]) == null ? void 0 : _f.id;
        await getTeamsMembers();
        return await getTeamApplications();
      } catch (e) {
      }
    };
    const getTeamsMembers = async () => {
      try {
        const res = await getTeamsMembersAPI({ team_id: form.team_id });
        if (res.code === 200) {
          form.team_users = res.data.map((i) => i.username).join(",");
        }
      } catch (e) {
      }
    };
    const getTeamApplications = async () => {
      try {
        const res = await getTeamApplicationsAPI({ team_id: form.team_id });
        return res;
      } catch (e) {
      }
    };
    const showCustomDialog = ref(false);
    const dialogContent = ref({
      content: "",
      confirmText: "",
      cancelText: "",
      confirmCallback: () => {
      },
      cancelCallback: () => {
      }
    });
    const toLogin = () => {
      const { getCurrentLocale } = useStore("locale");
      setItem(LOCALE_BEFORE_LOGIN_KEY, getCurrentLocale.value);
      router.push({ path: "/login", query: { redirect_url: encodeURIComponent(location.href) } });
    };
    const toRegister = () => {
      router.push({ path: "/Register", query: { raceId: __props.raceDetail.parent_rid, trackId: __props.raceDetail.rid } });
    };
    const isInitialLoad = ref(true);
    const showDialog = ({
      content,
      confirmText,
      confirmCallback = () => {
      },
      hideCancelButton = false
    }) => {
      dialogContent.value = {
        content,
        confirmText,
        cancelText: "",
        hideCancelButton,
        confirmCallback,
        cancelCallback: () => {
        }
      };
      showCustomDialog.value = true;
      formDisabled.value = true;
    };
    watch(
      () => resultStatus.value,
      async (val) => {
        if (val !== ComputingRequestStatusEnum.APPLY) return;
        if (isInitialLoad.value) return;
        getUserTeams();
      }
    );
    onMounted(async () => {
      var _a2, _b2, _c, _d, _e, _f, _g, _h, _i, _j, _k, _l, _m, _n, _o, _p, _q;
      if (!isLogin.value) {
        return;
      }
      pageLoading.value = true;
      const requestStatus = (_a2 = getComputeSchedule()) == null ? void 0 : _a2.status;
      const comStatus = (_b2 = getScheduleByCode("competition")) == null ? void 0 : _b2.status;
      if (requestStatus === RaceScheduleStatusEnum.ENDING && comStatus === RaceScheduleStatusEnum.ENDING) {
        const res = await rankList({ rid: __props.raceDetail.rid, tid: trackName, final: true });
        resultStatus.value = ((_c = res.data) == null ? void 0 : _c.length) > 0 ? ComputingRequestStatusEnum.COMPETITION_CLOSED : ComputingRequestStatusEnum.COMPETITION_WINDOW_CLOSED;
      } else {
        const res = await getUserTeams();
        if (requestStatus === RaceScheduleStatusEnum.UNOPEN) {
          resultStatus.value = ComputingRequestStatusEnum.UNSTARTED;
        } else {
          resultStatus.value = ComputingRequestStatusEnum.APPLY;
          if ((res == null ? void 0 : res.code) === 200 && ((_d = res.data) == null ? void 0 : _d.length)) {
            if (((_f = (_e = res.data) == null ? void 0 : _e[0]) == null ? void 0 : _f.status) === 1 && !hasResourceInstance.value) {
              resultStatus.value = ComputingRequestStatusEnum.PENDING;
            } else {
              const { resource_apply_rejected_count: resource_apply_rejected_count2, status } = ((_g = res.data) == null ? void 0 : _g[0]) || {};
              if (resource_apply_rejected_count2 === 1 && status === 2 && requestStatus === RaceScheduleStatusEnum.ENDING) {
                resultStatus.value = ComputingRequestStatusEnum.CLOSED;
              } else {
                resultStatus.value = (_i = (_h = res.data) == null ? void 0 : _h[0]) == null ? void 0 : _i.status;
              }
            }
            switch (resultStatus.value) {
              case ComputingRequestStatusEnum.PENDING:
              case ComputingRequestStatusEnum.PENDING2:
                schedulesTime.value = (_j = getComputeSchedule()) == null ? void 0 : _j.time_display;
                break;
              case ComputingRequestStatusEnum.APPROVED:
                phaseTine.value = (_l = (_k = res.data) == null ? void 0 : _k[0]) == null ? void 0 : _l.countdown_seconds;
                break;
              case ComputingRequestStatusEnum.REJECTED:
                resource_apply_rejected_count.value = (_m = res.data) == null ? void 0 : _m[0].resource_apply_rejected_count;
                reviewComment.value = ((_o = (_n = res.data) == null ? void 0 : _n[0]) == null ? void 0 : _o.review_comment) || ((_q = (_p = res.data) == null ? void 0 : _p[0]) == null ? void 0 : _q.review_comments) || "";
                break;
            }
          } else if (requestStatus === RaceScheduleStatusEnum.ENDING) {
            resultStatus.value = ComputingRequestStatusEnum.CLOSED;
          }
        }
      }
      pageLoading.value = false;
      isInitialLoad.value = false;
    });
    return (_ctx, _cache) => {
      const _component_svg_icon = _sfc_main$2;
      const _component_el_input = ElInput;
      const _component_el_form_item = ElFormItem;
      const _component_el_button = ElButton;
      const _component_el_form = ElForm;
      const _directive_loading = vLoading;
      return openBlock(), createElementBlock(Fragment, null, [
        withDirectives((openBlock(), createElementBlock("div", _hoisted_1, [
          createBaseVNode("div", _hoisted_2, [
            createVNode(_sfc_main$1, { raceId: unref(rid) }, null, 8, ["raceId"]),
            createBaseVNode("div", _hoisted_3, toDisplayString(unref(t)("s2Track2.timezoneTip")), 1)
          ]),
          prChecks.value.length ? (openBlock(), createBlock(SubmissionPrCheck, {
            key: 0,
            checks: prChecks.value,
            onLogin: toLogin,
            onRegister: toRegister
          }, null, 8, ["checks"])) : resultStatus.value !== unref(ComputingRequestStatusEnum).APPLY ? (openBlock(), createBlock(ComputingRequestResult, {
            key: 1,
            currentState: currentState.value
          }, null, 8, ["currentState"])) : (openBlock(), createElementBlock(Fragment, { key: 2 }, [
            !resource_apply_rejected_count.value ? (openBlock(), createElementBlock("div", _hoisted_4, [
              createVNode(_component_svg_icon, {
                name: "tips",
                class: "w-16 h-16 mt-2"
              }),
              createBaseVNode("span", null, toDisplayString(unref(t)("s2Track2.apply.noticeTip")), 1)
            ])) : (openBlock(), createElementBlock("div", _hoisted_5, [
              createBaseVNode("ul", _hoisted_6, [
                createBaseVNode("li", _hoisted_7, toDisplayString(unref(t)("s2Track2.apply.reviewCommentsLabel")) + " " + toDisplayString(reviewComment.value), 1),
                createBaseVNode("li", _hoisted_8, toDisplayString(unref(t)("s2Track2.apply.lastResubmitWarning")), 1)
              ])
            ])),
            createVNode(_component_el_form, {
              model: form,
              ref_key: "formRef",
              ref: formRef,
              rules,
              "label-width": "auto",
              "label-position": "top",
              class: "mt-16 w-100% flex flex-wrap gap-x-24"
            }, {
              default: withCtx(() => [
                createVNode(_component_el_form_item, {
                  label: unref(t)("computingRequest.teamName"),
                  class: "flex-1"
                }, {
                  default: withCtx(() => [
                    createVNode(_component_el_input, {
                      modelValue: form.team_name,
                      "onUpdate:modelValue": _cache[0] || (_cache[0] = ($event) => form.team_name = $event),
                      placeholder: unref(t)("computingRequest.placeholder"),
                      disabled: ""
                    }, null, 8, ["modelValue", "placeholder"])
                  ]),
                  _: 1
                }, 8, ["label"]),
                createVNode(_component_el_form_item, {
                  label: unref(t)("computingRequest.teamMembers"),
                  class: "flex-1"
                }, {
                  default: withCtx(() => [
                    createVNode(_component_el_input, {
                      modelValue: form.team_users,
                      "onUpdate:modelValue": _cache[1] || (_cache[1] = ($event) => form.team_users = $event),
                      placeholder: unref(t)("computingRequest.placeholder"),
                      disabled: ""
                    }, null, 8, ["modelValue", "placeholder"])
                  ]),
                  _: 1
                }, 8, ["label"]),
                createVNode(_component_el_form_item, {
                  label: unref(t)("computingRequest.applicationMaterial"),
                  prop: "files",
                  class: "w-100%"
                }, {
                  default: withCtx(() => [
                    createVNode(Upload, {
                      modelValue: form.files,
                      "onUpdate:modelValue": _cache[2] || (_cache[2] = ($event) => form.files = $event),
                      disabled: formDisabled.value,
                      accept: ".pdf",
                      "custom-validate-file": validateFileName
                    }, null, 8, ["modelValue", "disabled"]),
                    createBaseVNode("div", _hoisted_9, [
                      createBaseVNode("p", null, [
                        _cache[6] || (_cache[6] = createBaseVNode("span", { class: "w-20 inline-block" }, "1、", -1)),
                        createTextVNode(" " + toDisplayString(unref(t)("computingRequest.applicationMaterialTip1")), 1)
                      ]),
                      createBaseVNode("p", null, [
                        _cache[7] || (_cache[7] = createBaseVNode("span", { class: "w-20 inline-block" }, "2、", -1)),
                        createTextVNode(" " + toDisplayString(unref(t)("computingRequest.applicationMaterialTip2")) + '" ', 1),
                        createBaseVNode("strong", null, toDisplayString(unref(t)("computingRequest.applicationMaterialTip3", { accept: "pdf" })), 1),
                        _cache[8] || (_cache[8] = createTextVNode(' " ', -1))
                      ])
                    ])
                  ]),
                  _: 1
                }, 8, ["label"]),
                createVNode(_component_el_form_item, {
                  class: "mt-4",
                  label: ""
                }, {
                  default: withCtx(() => {
                    var _a2;
                    return [
                      createVNode(_component_el_button, {
                        class: "color-#fff bg-1 border-none",
                        type: "primary",
                        disabled: !((_a2 = form.files) == null ? void 0 : _a2.length) || formDisabled.value,
                        onClick: _cache[3] || (_cache[3] = ($event) => submit())
                      }, {
                        default: withCtx(() => [
                          createTextVNode(toDisplayString(unref(t)("computingRequest.submit")), 1)
                        ]),
                        _: 1
                      }, 8, ["disabled"]),
                      createVNode(_component_el_button, {
                        onClick: _cache[4] || (_cache[4] = ($event) => reset()),
                        type: "primary",
                        plain: "",
                        class: "px-16",
                        disabled: formDisabled.value
                      }, {
                        default: withCtx(() => [
                          createTextVNode(toDisplayString(unref(t)("computingRequest.reset")), 1)
                        ]),
                        _: 1
                      }, 8, ["disabled"])
                    ];
                  }),
                  _: 1
                })
              ]),
              _: 1
            }, 8, ["model"])
          ], 64))
        ])), [
          [_directive_loading, pageLoading.value]
        ]),
        createVNode(CustomDialog, {
          content: dialogContent.value.content,
          show: showCustomDialog.value,
          "onUpdate:show": _cache[5] || (_cache[5] = ($event) => showCustomDialog.value = $event),
          "dialog-content": dialogContent.value,
          title: unref(t)("computingRequest.tip")
        }, null, 8, ["content", "show", "dialog-content", "title"])
      ], 64);
    };
  }
});
const applyCompute = /* @__PURE__ */ _export_sfc(_sfc_main, [["__scopeId", "data-v-dcc012b9"]]);
export {
  applyCompute as default
};
//# sourceMappingURL=applyCompute-Br1APlpK.js.map
