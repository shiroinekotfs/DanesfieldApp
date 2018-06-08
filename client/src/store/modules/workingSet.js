export default {
    namespaced: true,
    state: {
      editingWorkingSet: null
    },
    mutations: {
      setEditingWorkingSet(state, workingSet) {
        state.editingWorkingSet = workingSet;
      }
    },
    actions: {},
    getters: {
      editingConditionsGeojson(state) {
        if (!state.editingConditions) {
          return null;
        }
        return {
          type: "FeatureCollection",
          features: state.editingConditions
            .filter(
              condition =>
                condition.type === "region" &&
                condition !== state.selectedCondition
            )
            .map(condition => condition.geojson)
        };
      },
      editingSelectedConditionGeojson(state) {
        if (
          !state.selectedCondition ||
          state.selectedCondition.type !== "region"
        ) {
          return null;
        }
        return state.selectedCondition.geojson;
      }
    }
  };